#!/usr/bin/env python3

# pefile.py
# PE definitions and helper functions
# See https://skr1x.github.io/portable-executable-format/

import struct
from typing import BinaryIO, Optional
from peconsts import ImageDirectoryType
from codeview import CodeViewDebugInfo

def align(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)

class PESection:
    section_header_struct = struct.Struct('<8sIIIIIIHHI')

    def __init__(self) -> None:
        self.sec_name: str = ''
        self.sec_len: int = 0
        self.data: bytearray = bytearray()
        self.virt_addr: int = 0
        self.file_offset: int = 0
        self.flags: int = 0

    def __repr__(self) -> str:
        return f'<Section {self.sec_name}: load address 0x{self.virt_addr:0x} length {self.sec_len:0x}>'

    @staticmethod
    def from_pe_file(file: bytearray, info_offset: int) -> 'PESection':
        sec = PESection()

        hdr = PESection.section_header_struct.unpack_from(file, info_offset)
        name, virtual_size, virtual_address, size_of_raw_data, pointer_to_raw_data, \
        pointer_to_relocations, pointer_to_linenumbers, number_of_relocations, \
        number_of_linenumbers, characteristics = hdr

        sec.sec_name = name.rstrip(b'\0').decode()
        sec.sec_len = virtual_size
        sec.virt_addr = virtual_address
        sec.file_offset = pointer_to_raw_data
        sec.flags = characteristics

        sec.data = file[pointer_to_raw_data:pointer_to_raw_data+size_of_raw_data]
        return sec

class DataDirectoryEntry:
    def __init__(self) -> None:
        self.data = bytearray()

    @staticmethod
    def read(pe: 'PE', file: bytearray, offset: int, size: int) -> 'DataDirectoryEntry':
        entry = DataDirectoryEntry()
        entry.data = file[offset:offset+size]
        return entry

class DebugDirectoryEntry(DataDirectoryEntry):
    header_struct = struct.Struct('<IIHHIIII')

    def __init__(self) -> None:
        super().__init__()
        self.codeview = CodeViewDebugInfo()

    @staticmethod
    def read(pe: 'PE', file: bytearray, offset: int, size: int) -> 'DebugDirectoryEntry':
        entry = DebugDirectoryEntry()
        hdr = DebugDirectoryEntry.header_struct.unpack_from(file, offset)
        characteristics, time_date_stamp, major_version, minor_version, type, \
        size_of_data, virtual_address_of_raw_data, pointer_of_raw_data = hdr
        if type == 2: # CodeView
            entry.codeview = CodeViewDebugInfo.read(pe, file, pointer_of_raw_data)
        return entry

data_directory_classes = {
    ImageDirectoryType.IMAGE_DIRECTORY_ENTRY_DEBUG: DebugDirectoryEntry
}

class PE:
    dos_header_struct = struct.Struct('<HHHHHHHHHHHHHH8xHH20xI')
    nt_header_struct = struct.Struct('<IHHIIIHH')
    nt_opt_header_struct = struct.Struct('<HBBIIIIIIIIIHHHHHHIIIIHHIIIIII')
    data_dir_struct = struct.Struct('<II')

    def __init__(self, file: Optional[BinaryIO]=None) -> None:
        self.entry: int = 0
        self.image_base: int = 0
        self.sections: list[PESection] = []
        self.data_directory: dict[ImageDirectoryType, DataDirectoryEntry] = {}

        if file:
            self.read(file)

    def rva_to_file_offset(self, rva: int) -> int:
        for sec in self.sections:
            if sec.virt_addr <= rva < sec.virt_addr + sec.sec_len:
                return sec.file_offset + (rva - sec.virt_addr)
        raise ValueError(f'RVA 0x{rva:x} does not belong to any section')

    def read(self, file: BinaryIO) -> None:
        bytes = bytearray(file.read())

        dos_hdr = self.dos_header_struct.unpack_from(bytes, 0)
        e_magic, e_cblp, e_cp, e_crlc, e_cparhdr, e_minalloc, e_maxalloc, e_ss, e_sp, \
        e_csum, e_ip, e_cs, e_lfarlc, e_ovno, e_oemid, e_oeminfo, e_lfanew = dos_hdr
        assert e_magic == int.from_bytes(b'MZ', 'little')

        nt_hdr = self.nt_header_struct.unpack_from(bytes, e_lfanew)
        signature, machine, number_of_sections, time_date_stamp, pointer_to_symbol_table, number_of_symbols, size_of_optional_header, characteristics = nt_hdr
        assert signature == int.from_bytes(b'PE\0\0', 'little')
        assert size_of_optional_header == self.nt_opt_header_struct.size + 16 * self.data_dir_struct.size

        nt_opt_hdr = self.nt_opt_header_struct.unpack_from(bytes, e_lfanew + self.nt_header_struct.size)
        magic, major_linker_ver, minor_linker_version, size_of_code, size_of_initialized_data, size_of_uninitialized_data, \
        address_of_entry_point, base_of_code, base_of_data, image_base, section_alignment, file_alignment, \
        major_os_version, minor_os_version, major_image_version, minor_image_version, major_subsystem_version, minor_subsystem_version, \
        win32_version_value, size_of_image, size_of_headers, checksum, subsystem, dll_characteristics, \
        size_of_stack_reserve, size_of_stack_commit, size_of_heap_reserve, size_of_heap_commit, loader_flags, number_of_rva_and_sizes = nt_opt_hdr
        assert magic == 0x10b

        self.entry = address_of_entry_point
        self.image_base = image_base

        sections_info_offset = e_lfanew + self.nt_header_struct.size + size_of_optional_header

        for i in range(number_of_sections):
            offset = sections_info_offset + i * 40
            self.add_section(PESection.from_pe_file(bytes, offset))

        data_dir_offset = e_lfanew + self.nt_header_struct.size + self.nt_opt_header_struct.size
        for i in range(number_of_rva_and_sizes):
            offset = data_dir_offset + i * self.data_dir_struct.size
            entry_type = ImageDirectoryType(i)
            rva, size = self.data_dir_struct.unpack_from(bytes, offset)
            if size == 0:
                continue
            cls = DataDirectoryEntry
            if entry_type in data_directory_classes:
                cls = data_directory_classes[entry_type]
            offset = self.rva_to_file_offset(rva)
            self.data_directory[entry_type] = cls.read(self, bytes, offset, size)

        self.bss_addr, self.bss_len, self.entry = struct.unpack_from('>III', bytes, 0xD8)

    def add_section(self, section: PESection) -> None:
        self.sections.append(section)
