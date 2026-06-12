#pragma once

#include <common.h>

extern Handle COS_NewHandle(SInt32 byteCount);
extern Handle COS_NewOSHandle(SInt32 logicalSize);
extern void COS_FreeHandle(Handle handle);
extern Boolean COS_ResizeHandle(Handle handle, SInt32 newSize);
extern SInt32 COS_GetHandleSize(Handle handle);
extern void COS_LockHandle(Handle handle);
extern void COS_LockHandleHi(Handle handle);
extern void COS_UnlockHandle(Handle handle);
extern int COS_GetHandleState(Handle handle);
extern void COS_SetHandleState(Handle handle, int state);
extern Boolean COS_IsLockedState(int state);
extern char *COS_NewPtr(SInt32 byteCount);
extern char *COS_NewPtrClear(SInt32 byteCount);
extern void COS_FreePtr(char *ptr);
extern void COS_AppendPtrToHandle(char *ptr1, Handle hand2, SInt32 size);
extern OSErr COS_GetMemErr(void);
extern SInt32 COS_GetTicks(void);
extern SInt32 COS_GetTime(void);
extern void COS_GetString(char *buffer, SInt16 strListID, SInt16 index);
extern void COS_GetPString(StringPtr buffer, SInt16 strListID, SInt16 index);
extern Boolean COS_IsMultiByte(const void *str1, const void *str2);
extern OSErr COS_FileNew(const FSSpec *spec, SInt16 *refNum, OSType creator, OSType fileType);
extern OSErr COS_FileOpen(const FSSpec *spec, SInt16 *refNum);
extern OSErr COS_FileGetType(const FSSpec *spec, OSType *fileType);
extern OSErr COS_FileGetSize(SInt16 refNum, SInt32 *logEOF);
extern OSErr COS_FileRead(SInt16 refNum, void *buffPtr, SInt32 count);
extern OSErr COS_FileWrite(SInt16 refNum, const void *buffPtr, SInt32 count);
extern OSErr COS_FileGetPos(SInt16 refNum, SInt32 *filePos);
extern OSErr COS_FileSetPos(SInt16 refNum, SInt32 filePos);
extern OSErr COS_FileClose(SInt16 refNum);
extern void COS_FileSetFSSpec(FSSpec *spec, ConstStringPtr path);
extern OSErr COS_FileMakeFSSpec(SInt16 vRefNum, SInt32 dirID, ConstStringPtr fileName, FSSpec *spec);
extern OSErr COS_FileMakeFSSpecWithPath(const FSSpec *inputSpec, ConstStringPtr fileName, FSSpec *spec);
extern OSErr COS_FileGetFileInfo(const FSSpec *spec, OSType *creator, OSType *fileType);
extern void COS_FileGetFSSpecInfo(const FSSpec *spec, SInt16 *vRefNum, SInt32 *dirID, StringPtr fileName);
extern void COS_FileGetPathName(char *buffer, const FSSpec *spec, SInt32 *mdDat);
extern int COS_EqualFileSpec(const FSSpec *a, const FSSpec *b);
