
/**
 * Compile:
 * arm-linux-gnueabi-gcc compromised-reboot.c -o compromised-reboot -static
 *
 * REMEMBER TO RUN AS ROOT!
 */

#include <unistd.h>
#include <sys/reboot.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>

int main()
{

  while (1) {
    sleep(1); // loop every second

    // check if the sd card appears missing
    struct stat st;
    int removed = stat("/sys/block/mmcblk0", &st);

    if (removed) {
      // reboot when drive is missing
      printf("Compromise detected\n");
      reboot(RB_AUTOBOOT);
    }
  }

}
