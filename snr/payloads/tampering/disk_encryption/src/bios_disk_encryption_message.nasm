bits 16
org 0x7c00

.print_message:
    mov si, message
.print_message_loop:
    mov ah, 0x0e
    lodsb
    cmp al, 0 
    je .halt
    int 0x10
    jmp .print_message_loop
.halt:
    hlt

message:
    db "This device has been encrypted. Continuing boot is not possible."
    ; We are intentionally not putting a null-byte here.
    ; This allows the payload generation process 
    ; to add to this message a custom message of at most size COUNT_OF_ZEROS-1

times 446-($-$$) db 0 ; Why not 512? Reserve space for the partition table

