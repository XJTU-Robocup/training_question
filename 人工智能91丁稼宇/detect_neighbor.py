import cv2 as cv
import numpy as np
from time import time
#视频读入与输出
getvideo=cv.VideoCapture("video.mp4")
fps=getvideo.get(cv.CAP_PROP_FPS)
width=int(getvideo.get(cv.CAP_PROP_FRAME_WIDTH))
height=int(getvideo.get(cv.CAP_PROP_FRAME_HEIGHT))
writevideo=cv.VideoWriter("detected.avi",cv.CAP_FFMPEG,cv.VideoWriter_fourcc(*"MJPG"),fps,(width,height))

#算法思想
#1.在HSV空间判断是否为绿色
#2.盘子没有出现时，全图搜索绿色区域
#3.盘子出现后，在上一帧盘子位置的邻域寻找当前盘子位置（增快程序速度）
#4.如果当前盘子的识别框与邻域框接近，认为邻域框可能没有框住盘子，重新全图搜索(针对运动速度较快)
#优点
#1.识别框标记准确
#2.平均速度可以达到近实时（运行2.6ms，含读入输出5.9ms）
#缺点
#1.基于绿色的判断仅适用于背景非绿的情况
#2.切换到全图搜索时远慢于实时（运行14.6ms，含读入输出17.3ms）
#3.有一定数量参数
processtime=[]#运行时间
ifhide=True#盘子是否“没有出现”
hsvlow=np.array([50,100,100])#hsv空间中绿色对应范围
hsvhigh=np.array([77,255,255])
aroundborder=[0,0,0,0]
around=30#邻域延伸长度
eps=5#两框距离阈值
while True:
    procstart=time()
    ifnotend,frame=getvideo.read()
    if(ifnotend): 
        hsv=cv.cvtColor(frame,cv.COLOR_BGR2HSV)
        #注释部分可视化图片哪些部分被识别为绿色
        #ifgreen=np.zeros((height,width))
        #ifgreen[np.all(hsv>=hsvlow,2) & np.all(hsv<=hsvhigh,2)]=255
        #cv.imshow("",ifgreen)
        #cv.waitKey( )
        if ifhide:
            #全图搜索
            pos=np.argwhere(np.all(hsv>=hsvlow,2) & np.all(hsv<=hsvhigh,2))
        else:
            #邻域搜索
            aroundborder=[max(xmin-around,0),min(xmax+around,height),max(ymin-around,0),min(ymax+around,height)]
            aroundimg=hsv[aroundborder[0]:aroundborder[1],aroundborder[2]:aroundborder[3],:]
            pos=np.argwhere(np.all(aroundimg>=hsvlow,2) & np.all(aroundimg<=hsvhigh,2))
        if(pos.shape[0]>=4):
            #确定识别框
            xmin=aroundborder[0]+np.min(pos[:,0])
            xmax=aroundborder[0]+np.max(pos[:,0])
            ymin=aroundborder[2]+np.min(pos[:,1])
            ymax=aroundborder[2]+np.max(pos[:,1])
            if (not ifhide) and (xmin<aroundborder[0]+eps or ymin<=aroundborder[2]+eps or xmax>=aroundborder[1]-eps or ymax>=aroundborder[3]-eps):
                #重新全图搜索
                pos=np.argwhere(np.all(hsv>=hsvlow,2) & np.all(hsv<=hsvhigh,2))
                xmin=np.min(pos[:,0])
                xmax=np.max(pos[:,0])
                ymin=np.min(pos[:,1])
                ymax=np.max(pos[:,1])
            ifhide=False

            #绘制识别框
            cv.rectangle(frame,(ymin,xmin),(ymax,xmax),(0,255,0))
            cv.putText(frame,"green",(ymin,xmin-8),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0))
            writevideo.write(frame)
            processtime.append(time()-procstart)
        else:
            ifhide=True
            aroundborder=[0,0,0,0]
    else: break
getvideo.release()
writevideo.release()
print(np.mean(processtime))