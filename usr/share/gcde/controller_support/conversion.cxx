/*
 * conversion.cxx
 *
 * Copyright 2020 Thomas Castleman <contact@draugeros.org>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 *
 *
 */


 #include <stdio.h>
 #include <unistd.h>
 #include <errno.h>
 #include <regex.h>
 #include <dirent.h>
 #include <fcntl.h>
 #include <linux/input.h>
 #include <stdbool.h>
 #include <stdint.h>
 #include <sys/time.h>

using namespace std;

bool pressKeys( void )
{
    static int keyboardFd = -1;
    int rd,n;
    bool ret = false;

    DIR *dirp;
    struct dirent *dp;
    regex_t kbd;

    char fullPath[1024];
    static char *dirName = "/dev/input/by-id";

    int result;
    struct input_event forcedKey;


    // Send ls<ret>
    uint16_t keys[] = {KEY_LEFT,KEY_RIGHT,KEY_UP,KEY_DOWN};
    int index;

    /* Find the device with a name ending in "event-kbd" */

    if(regcomp(&kbd,"event-kbd",0)!=0)
    {
        printf("regcomp for kbd failed\n");
        return false;

    }
    if ((dirp = opendir(dirName)) == NULL) {
        perror("couldn't open '/dev/input/by-id'");
        return false;
    }


    do {
        errno = 0;
        if ((dp = readdir(dirp)) != NULL)
        {
            printf("readdir (%s)\n",dp->d_name);
            if(regexec (&kbd, dp->d_name, 0, NULL, 0) == 0)
            {
                printf("match for the kbd = %s\n",dp->d_name);
                sprintf(fullPath,"%s/%s",dirName,dp->d_name);
                keyboardFd = open(fullPath,O_WRONLY | O_NONBLOCK);
                printf("%s Fd = %d\n",fullPath,keyboardFd);
                printf("Getting exclusive access: ");
                result = ioctl(keyboardFd, EVIOCGRAB, 1);
                printf("%s\n", (result == 0) ? "SUCCESS" : "FAILURE");

            }


        }
    } while (dp != NULL);

    closedir(dirp);


    regfree(&kbd);


    /* Now write some key press and key release events to the device */


    index = 0;
    while(keys[index] != 0)
    {

        forcedKey.type = EV_KEY;
        forcedKey.value = 1;    // Press
        forcedKey.code = keys[index];
        gettimeofday(&forcedKey.time,NULL);

        n = write(keyboardFd,&forcedKey,sizeof(struct input_event));
        printf("n=%d\n",n);

        forcedKey.type = EV_KEY;
        forcedKey.value = 0 ;   // Release
        forcedKey.code = keys[index];
        gettimeofday(&forcedKey.time,NULL);

        n = write(keyboardFd,&forcedKey,sizeof(struct input_event));
        printf("n=%d\n",n);

        index += 1;
    }

    close(keyboardFd);

    return(true);

}

int main(int argc, char **argv)
{
	pressKeys();
	return 0;
}
