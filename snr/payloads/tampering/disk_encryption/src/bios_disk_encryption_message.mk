NASM :=nasm
NASM_FLAGS :=
default: build

build: bios_disk_encryption_message.bin

bios_disk_encryption_message.bin:
	$(NASM) -f bin $(NASM_FLAGS) bios_disk_encryption_message.nasm -o bios_disk_encryption_message.bin

clean:
	rm -f bios_disk_encryption_message.bin
