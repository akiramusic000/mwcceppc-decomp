#ifndef COMPILER_CDECL_H
#define COMPILER_CDECL_H

#include <compiler/common.h>
#include <compiler/tokens.h>
#include <compiler/types.h>

#ifdef __MWERKS__
#pragma options align=mac68k
#endif

struct ClassLayout {
    ObjBase **objlist;
    ObjMemberVar *vtable_ivar;
    UInt16 lex_order_count;
    UInt16 xA;
    Boolean has_vtable;
};

struct DeclInfo {
    Type *thetype;
    UInt32 qual;
    NameSpace *nspace;
    HashNameNode *name;
    Object *x10;
    NameSpaceObjectList *x14;
    FuncArg *x18;
    NameSpace *x1C;
    Type *x20;
    ENode *x24;
    TemplClass *x28;
    TemplArg *expltargs;
    TemplParam *x30;
    DeclFucker *fucker34;
    TemplateFunction *x38;
    UInt8 x3C; // related to template nindex
    short operator_token; // when an operator name like "operator +" is scanned, this is the token
    short storageclass;
    UInt8 section;
    UInt8 exportflags;
    Boolean x44; // has args in identifier list
    Boolean x45; // has oldstyle args
    Boolean x46;
    Boolean x47;
    Boolean x48;
    Boolean x49;
    Boolean x4A; // objc related
    Boolean x4B;
    Boolean in_friend_decl; // set to 1 when parsing a 'friend' declaration
    Boolean x4D;
    Boolean is_extern_c;
    Boolean x4F;
    Boolean x50;
    Boolean x51;
    Boolean has_expltargs;
    Boolean x53;
    Boolean x54;
    Boolean x55;
    Boolean x56;
    Boolean x57;
    CPrepFileInfo *file;
    CPrepFileInfo *file2;
    SInt32 sourceoffset;
    Boolean x64;
};

typedef struct BigDeclInfo {
    DeclInfo declinfo;
    DeclInfo declinfo2;
    Boolean xCC;
    Boolean xCD;
} BigDeclInfo;

extern AccessType global_access;
extern FileOffsetInfo member_fileoffset;

extern Type *CDecl_NewStructType(SInt32 size, SInt16 align);
extern Type *CDecl_NewArrayType(Type *type, SInt32 size);
extern Type *CDecl_NewPointerType(Type *type);
extern Type *CDecl_NewRefPointerType(Type *type);
extern Type *CDecl_NewTemplDepType(TypeTemplDepType tdt);
extern Type *CDecl_NewOpaqueType(SInt32 size, SInt16 align);
extern void CDecl_SetResultReg(TypeFunc *tfunc);
extern void CDecl_SetFuncFlags(TypeFunc *tfunc, UInt32 flags);
extern void CDecl_NewConvFuncType(DeclInfo *declinfo);
extern void CDecl_CompleteType(Type *type);
extern Boolean IsCompleteType(Type *type);
extern Boolean CanAllocObject(Type *type);
extern Boolean CanCreateObject(Type *type);
extern void makethetypepointer(DeclInfo *declinfo, UInt32 qual);
extern void CDecl_AddThisPointerArgument(TypeFunc *tfunc, TypeClass *tclass);
extern void CDecl_MakePTMFuncType(TypeFunc *tfunc);
extern void CDecl_AddArgument(TypeFunc *tfunc, Type *argtype);
extern Boolean CDecl_CheckArrayIntegr(Type *type);
extern void CDecl_ParseDirectFuncDecl(DeclInfo *declinfo);
extern void makememberpointertype(DeclInfo *declinfo, TypeClass *tclass, UInt32 qual);
extern void CDecl_ScanPointer(DeclInfo *declinfo, NameSpace *nspace, Boolean flag);
extern void scandeclarator(DeclInfo *declinfo);
extern void conversion_type_name(DeclInfo *declinfo);
extern void MergeDefaultArgs(FuncArg *a, FuncArg *b);
extern void CheckDefaultArgs(FuncArg *args);
extern Object *CDecl_GetFunctionObject(DeclInfo *declinfo, NameSpace *nspace, Boolean *pflag, Boolean someotherflag);
extern void CDecl_TypedefDeclarator(DeclInfo *declinfo);
extern Boolean CDecl_FunctionDeclarator(DeclInfo *declinfo, NameSpace *nspace, Boolean flag, Boolean flag2);
extern void CDecl_ScanDeclarator(DeclInfo *declinfo);
extern void scandeclaratorlist(DeclInfo *declinfo);
extern void CDecl_ComputeUnderlyingEnumType(TypeEnum *tenum);
extern void scanenum(DeclInfo *declinfo);
extern void CDecl_ScanStructDeclarator(BigDeclInfo *bde);
extern void scanstruct(DeclInfo *declinfo, short structtype);
extern void CDecl_ExtractClassExportFlags(DeclInfo *declinfo, UInt8 flags);
extern TypeMemberFunc *CDecl_MakeTypeMemberFunc(TypeFunc *tfunc, TypeClass *tclass, Boolean flag);
extern void CDecl_PackDeclInfo(PackedDeclInfo *packed, DeclInfo *declinfo);
extern void CDecl_UnpackDeclInfo(DeclInfo *declinfo, PackedDeclInfo *packed);
extern void CDecl_AddFriend(TypeClass *tclass, Object *friendfunc, TypeClass *friendclass);
extern void CDecl_CheckCtorIntegrity(FuncArg *args, TypeClass *tclass);
extern void CDecl_MakeVBaseList(TypeClass *tclass);
extern Boolean CDecl_CheckNewBase(TypeClass *tclass, TypeClass *baseclass, Boolean is_virtual);
extern TypeMemberFunc *CDecl_MakeDefaultDtorType(TypeClass *tclass, Boolean is_virtual);
extern void CDecl_CompleteClass(ClassLayout *layout, TypeClass *tclass);
extern TypeClass *CDecl_DefineClass(NameSpace *nspace, HashNameNode *name, TypeClass *tclass, short mode, Boolean flag2, Boolean flag3);
extern void CDecl_ParseClassDeclSpec(UInt8 *declspec);
extern void CDecl_ParseClass(DeclInfo *declinfo, short mode, Boolean flag1, UInt8 class_declspec);

#ifdef __MWERKS__
#pragma options align=reset
#endif

#endif
