#!/usr/bin/env python3

# codeview.py
# CodeView debug information parsing

import struct
from peconsts import CVSubsection

import typing
if typing.TYPE_CHECKING:
    from pefile import PE

def align(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)

class CodeViewModule:
    header_struct = struct.Struct('<HHH2s')
    seg_struct = struct.Struct('<H2xII')

    def __init__(self) -> None:
        self.name: str = ''
        self.obj_file_name: str = ''

    @staticmethod
    def read(file: bytearray, offset: int) -> 'CodeViewModule':
        mod = CodeViewModule()
        hdr = CodeViewModule.header_struct.unpack_from(file, offset)
        ovl_number, i_lib, c_seg, style = hdr
        pos = offset + CodeViewModule.header_struct.size
        for i in range(c_seg):
            seg_hdr = CodeViewModule.seg_struct.unpack_from(file, pos)
            seg_idx, off, c_b_seg = seg_hdr
            # print(f'Segment {seg_idx} offset 0x{off:x} size 0x{c_b_seg:x}')
            pos += CodeViewModule.seg_struct.size
        name_len = file[pos]
        pos += 1
        name = file[pos:pos + name_len].decode()
        # print(f'{name} {ovl_number} {i_lib} {c_seg} {style}')
        return mod

def read_lstring(file: bytearray, offset: int) -> tuple[str, int]:
    length = file[offset]
    offset += 1
    return file[offset:offset + length].decode(), offset + length

class CodeViewSyms:
    def __init__(self) -> None:
        self.symbols: list[tuple[int, int, str]] = []

    @staticmethod
    def read(pe: 'PE', file: bytearray, offset: int, size: int) -> 'CodeViewSyms':
        mod = CodeViewSyms()

        pos = offset + 4
        while pos < offset + size:
            old_pos = pos
            sym_len, sym_type = struct.unpack_from('<HH', file, pos)
            pos += 4
            match sym_type:
                case 1:
                    machine_info, flags = struct.unpack_from('<BxH', file, pos)
                    pos += 4
                    compiler_version, pos = read_lstring(file, pos)
                    # print(f'Compiler version {compiler_version} machine {machine_info:x} flags {flags:x}')
                case 0x1007 | 0x1008 | 0x1009:
                    ty, seg_offset, segment = struct.unpack_from('<IIH', file, pos)
                    pos += 10
                    name, pos = read_lstring(file, pos)
                    mod.symbols.append((segment - 1, seg_offset, name))
                case _:
                    # print(f'Unknown symbol type {sym_type:x}')¨
                    pass
            pos = old_pos + 2 + sym_len

        return mod

class CodeViewDebugInfo:
    header_struct = struct.Struct('<4sI')
    dir_header_struct = struct.Struct('<HHIII')
    dir_entry_struct = struct.Struct('<HHII')

    def __init__(self):
        self.modules: list[CodeViewSyms] = []

    @staticmethod
    def read(pe: 'PE', file: bytearray, offset: int) -> 'CodeViewDebugInfo':
        info = CodeViewDebugInfo()

        hdr = CodeViewDebugInfo.header_struct.unpack_from(file, offset)
        sig, data_offset = hdr
        assert sig == b'NB11'

        subsection_data = CodeViewDebugInfo.dir_header_struct.unpack_from(file, offset + data_offset)
        b_dir_header, b_dir_entry, c_dir, lfo_next_dir, flags = subsection_data
        assert b_dir_header == CodeViewDebugInfo.dir_header_struct.size
        assert b_dir_entry == CodeViewDebugInfo.dir_entry_struct.size
        assert lfo_next_dir == 0

        dir_entry_offset = offset + data_offset + CodeViewDebugInfo.dir_header_struct.size
        for i in range(c_dir):
            dir_offset = dir_entry_offset + i * CodeViewDebugInfo.dir_entry_struct.size
            dir_entry = CodeViewDebugInfo.dir_entry_struct.unpack_from(file, dir_offset)
            _subsection_type, i_mod, lfo, c_b = dir_entry
            subsection_type = CVSubsection(_subsection_type)
            # print(f'Subsection {subsection_type.name} mod {i_mod} offset 0x{offset + lfo:x} size 0x{c_b:x}')
            match subsection_type:
                case CVSubsection.Module:
                    mod = CodeViewModule.read(file, offset + lfo)
                    # print(mod)
                case CVSubsection.AlignSym | CVSubsection.GlobalPub:
                    if subsection_type == CVSubsection.GlobalPub:
                        lfo += 12
                    mod = CodeViewSyms.read(pe, file, offset + lfo, c_b)
                    info.modules.append(mod)
                    # print(mod)
                case _:
                    pass

        return info
