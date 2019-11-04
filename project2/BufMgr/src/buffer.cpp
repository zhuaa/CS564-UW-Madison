
/**
 * @author See Contributors.txt for code contributors and overview of BadgerDB.
 *
 * @section LICENSE
 * Copyright (c) 2012 Database Group, Computer Sciences Department, University of Wisconsin-Madison.
 */

#include <memory>
#include <iostream>
#include "buffer.h"
#include "exceptions/buffer_exceeded_exception.h"
#include "exceptions/page_not_pinned_exception.h"
#include "exceptions/page_pinned_exception.h"
#include "exceptions/bad_buffer_exception.h"
#include "exceptions/hash_not_found_exception.h"

namespace badgerdb { 

BufMgr::BufMgr(std::uint32_t bufs)
  : numBufs(bufs) {
  bufDescTable = new BufDesc[bufs];

  for (FrameId i = 0; i < bufs; i++) 
  {
    bufDescTable[i].frameNo = i;
    bufDescTable[i].valid = false;
  }

  bufPool = new Page[bufs];

  int htsize = ((((int) (bufs * 1.2))*2)/2)+1;
  hashTable = new BufHashTbl (htsize);  // allocate the buffer hash table

  clockHand = bufs - 1;
}


BufMgr::~BufMgr() {
  for(int i=0; i<numBufs; i++){
    if(bufDescTable[i].valid && bufDescTable[i].dirty) 
      flushFile(bufDescTable[i].file);  //
  }
  delete hashTable;
  delete[] bufPool;
  delete[] bufDescTable;

}

void BufMgr::advanceClock()
{
  clockHand = (clockHand+1) % numBufs;

}

void BufMgr::allocBuf(FrameId & frame) 
{

  std::cout<< "allocate buffer"<<std::endl;
  clockHand = frame;
  unsigned int i = 0;
  while(i < numBufs * 2){
    if(!bufDescTable[clockHand].valid){
      frame = clockHand;
      return;
    }

    if(bufDescTable[clockHand].refbit){
      bufDescTable[clockHand].refbit = false;
      advanceClock();
      i++;
      continue;
    }

    else{

      if(bufDescTable[clockHand].pinCnt != 0){
        advanceClock();
        i++;
        continue;
      }
      else{
        if(bufDescTable[clockHand].dirty) bufDescTable[clockHand].file->writePage(bufPool[clockHand]);
        hashTable->remove(bufDescTable[clockHand].file, bufDescTable[clockHand].pageNo);
        bufDescTable[clockHand].Clear();
        frame  = clockHand;
        return;
      }
    }
  }

  throw BufferExceededException();

}

  
void BufMgr::readPage(File* file, const PageId pageNo, Page*& page)
{
  std::cout<< "read page"<< std::endl;
  FrameId frameNo;
  try{
    hashTable->lookup(file, pageNo, frameNo);
    bufDescTable[frameNo].refbit = true;
    bufDescTable[frameNo].pinCnt++;
    page = &bufPool[frameNo];
  }
  catch(HashNotFoundException e){
    allocBuf(clockHand);
    bufPool[clockHand] = file->readPage(pageNo);
    page = &bufPool[clockHand];
    hashTable->insert(file, page->page_number(), clockHand);
    bufDescTable[clockHand].Set(file, page->page_number());
    return;
  }


}


void BufMgr::unPinPage(File* file, const PageId pageNo, const bool dirty) 
{
  //std::cout<< "unPin page"<<std::endl;
  FrameId frameNo = numBufs;
  hashTable->lookup(file, pageNo, frameNo);
  if(frameNo != numBufs){
    if(bufDescTable[frameNo].pinCnt != 0){
      bufDescTable[frameNo].pinCnt--;
      if(dirty)
        bufDescTable[frameNo].dirty  = true;
    }
    else if(bufDescTable[frameNo].pinCnt == 0){
      throw PageNotPinnedException(file->filename(), pageNo, frameNo);
    }
  }

}

void BufMgr::flushFile(const File* file) 
{
  //std::cout<<"flush file"<<std::endl;
  for(FrameId i=0; i<numBufs; i++){
    if(bufDescTable[i].file != file) continue;
    if(bufDescTable[i].valid == false) throw BadBufferException(i, bufDescTable[i].dirty, bufDescTable[i].valid, bufDescTable[i].refbit);
    if(bufDescTable[i].pinCnt != 0) throw PagePinnedException(file->filename(), bufDescTable[i].pageNo, i);
    
    if(bufDescTable[i].dirty){
      bufDescTable[i].file->writePage(bufPool[i]);
      bufDescTable[i].dirty = false;
    }
    hashTable->remove(file, bufDescTable[i].pageNo);
    bufDescTable[i].Clear();
  }

}

void BufMgr::allocPage(File* file, PageId &pageNo, Page*& page) 
{
  
  //std::cout<<"allocate page"<<std::endl;
  FrameId frameNum = clockHand; 
  allocBuf(frameNum);
  bufPool[frameNum] = file->allocatePage();
  page = &bufPool[frameNum];
  pageNo = page->page_number();
  hashTable->insert(file, pageNo, frameNum);
  bufDescTable[frameNum].Set(file, pageNo);
}

void BufMgr::disposePage(File* file, const PageId PageNo)
{
  //std::cout<<"disposePage"<<std::endl;
  FrameId frameNo;
  try{
    hashTable->lookup(file, PageNo, frameNo);
    if(bufDescTable[frameNo].pinCnt != 0){
      throw PagePinnedException(bufDescTable[frameNo].file->filename(), bufDescTable[frameNo].pageNo, bufDescTable[frameNo].frameNo);
    }
    bufDescTable[frameNo].Clear();
    hashTable->remove(file, PageNo);
    file->deletePage(PageNo);
    return;
  }
  catch(HashNotFoundException e){
    file->deletePage(PageNo);
  }
}

void BufMgr::printSelf(void) 
{
  BufDesc* tmpbuf;
  int validFrames = 0;
  
  for (std::uint32_t i = 0; i < numBufs; i++)
  {
    tmpbuf = &(bufDescTable[i]);
    std::cout << "FrameNo:" << i << " ";
    tmpbuf->Print();

    if (tmpbuf->valid == true)
      validFrames++;
  }

  std::cout << "Total Number of Valid Frames:" << validFrames << "\n";
}

}


