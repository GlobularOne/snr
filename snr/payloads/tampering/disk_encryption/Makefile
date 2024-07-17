all: build

build: src/efi_disk_encryption_message.efi src/bios_disk_encryption_message.bin
	mkdir -p data
	cp src/efi_disk_encryption_message.efi data/EFIBOOTX64.EFI
	cp src/bios_disk_encryption_message.bin data/bios_disk_encryption_message.bin

src/uefi:
	git clone --no-checkout git@gitlab.com:bztsrc/posix-uefi.git src/posix-uefi
	git -C src/posix-uefi sparse-checkout set --no-cone '/uefi/*'
	git -C src/posix-uefi checkout
	cp -r src/posix-uefi/uefi src/uefi
	rm -rf src/posix-uefi

src/efi_disk_encryption_message.efi: src/uefi
	$(MAKE) -C src -f efi_disk_encryption_message.mk

src/bios_disk_encryption_message.bin:
	$(MAKE) -C src -f bios_disk_encryption_message.mk

clean:
	$(MAKE) -C src -f efi_disk_encryption_message.mk clean
	$(MAKE) -C src -f bios_disk_encryption_message.mk clean
	rm -rf payload_set src/posix-uefi src/uefi
