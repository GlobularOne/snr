#include "uefi/uefi.h"

int main(int argc, char **argv)
{
    char message_storage[1025];
    FILE* message_fp = NULL;
    char* message = NULL; 
    /* Retrieve the custom message */
    message_fp = fopen("message.txt", "r");
    if (message_fp != NULL)
    {
        memset(&message_storage[0], 0, sizeof(message_storage));
        fseek(message_fp, 0, SEEK_END);
        long message_size = ftell(message_fp);
        if (message_size > sizeof(message_storage) - 1)
        {
            /* Or in simpler words, truncate it */
            message_size = sizeof(message_storage) - 1;
        }
        fread(&message_storage[0], 1, message_size, message_fp);
        message = &message_storage[0];
    }
    printf("This device has been encrypted. Continuing boot is not possible\r\n");
    if (message != NULL)
    {
        printf("%s\r\n", message);
    }
    while (1)
    {
        asm("");
        sleep(60);
    }
    return 0;
}

