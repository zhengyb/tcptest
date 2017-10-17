#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <netdb.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>

int main(int argc,char *argv[])
{
    int sockfd;
    char sendbuffer[2000];
    char recvbuffer[2000];
  //  char buffer[1024];
    struct sockaddr_in server_addr;
    struct hostent *host;
    int portnumber,nbytes;
    int min_length = 1, max_length = 1420, method_id = 0;
    int ret;
    int flags;

    if(argc < 2){
        fprintf(stderr,"Usage :%s <server_addr> [<server_port> <min_length> <max_length> <method_Id>]\n",argv[0]);
        exit(1);
    }

    host = gethostbyname(argv[1]);
    if(argc > 2)
        if((portnumber = atoi(argv[2])) < 0){
            fprintf(stderr,"Usage :%s <server_addr> [<server_port> <min_length> <max_length> <method_Id>]\n",argv[0]);
            exit(1);
        }

    if(argc > 3)
        if((min_length = atoi(argv[3])) < 0){
            fprintf(stderr,"Usage :%s <server_addr> [<server_port> <min_length> <max_length> <method_Id>]\n",argv[0]);
            exit(1);
        }

    if(argc > 4)
        if((max_length = atoi(argv[4])) < 0){
            fprintf(stderr,"Usage :%s <server_addr> [<server_port> <min_length> <max_length> <method_Id>]\n",argv[0]);
            exit(1);
        }

    if(argc > 5)
        if((method_id = atoi(argv[5])) < 0){
            fprintf(stderr,"Usage :%s <server_addr> [<server_port> <min_length> <max_length> <method_Id>]\n",argv[0]);
            exit(1);
        }


    if((sockfd=socket(AF_INET,SOCK_STREAM,0))==-1){
        fprintf(stderr,"Socket Error:%s\a\n",strerror(errno));
        exit(1);
    }

    bzero(&server_addr,sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(portnumber);
    server_addr.sin_addr = *((struct in_addr *)host->h_addr);
    if(connect(sockfd,(struct sockaddr *)(&server_addr),sizeof(struct sockaddr))==-1){
        fprintf(stderr,"Connect error:%s\n",strerror(errno));
        exit(1);
    }

    printf("connected\n");

    flags  = fcntl(sockfd,F_GETFL,0);
    fcntl(sockfd,F_SETFL,flags & ~O_NONBLOCK); 

    sprintf(sendbuffer, "cmd:%d,%d,%d", min_length, max_length, method_id);
    send(sockfd, sendbuffer, strlen(sendbuffer), 0);
    sleep(3);

    while(1){
        memset(recvbuffer, 0, sizeof(recvbuffer));
        ret = recv(sockfd, recvbuffer, 2000, 0);
        if (ret == 0){
            printf("No more data\n");
            break;
        }else if(ret > 0){
            printf("recv %d bytes.\n", ret);
            if (strncmp(recvbuffer, "exit", 4) == 0){
                printf("exit\n");
                break;
            }

            send(sockfd, recvbuffer, strlen(recvbuffer),0);
            
        }else{
            printf("recv error\n");
            break;
        }
    }
   // if((nbytes=read(sockfd,buffer,1024))==-1)
    //{
// fprintf(stderr,"read error:%s\n",strerror(errno));
// exit(1);
  //  }
   // buffer[nbytes]='\0';
   // printf("I have received %s\n",buffer);
    close(sockfd);
    exit(0);
}