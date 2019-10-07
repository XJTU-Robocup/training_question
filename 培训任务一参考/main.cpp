#include <opencv2/opencv.hpp>
#include <iostream>

using namespace std;
using namespace cv;

Rect roi;//������Ӿ���
void processFrame(Mat &binary, Rect &rect);//�����β�

int main(int argc, char* argv) {
	// load video
	VideoCapture capture;
	capture.open("test.mp4");

	if (!capture.isOpened()) {
		printf("could not find video file");
		return -1;
	}
	
	Mat frame, mask;
	Mat kernel1 = getStructuringElement(MORPH_RECT, Size(3, 3), Point(-1, -1));
	Mat kernel2 = getStructuringElement(MORPH_RECT, Size(5, 5), Point(-1, -1));

	namedWindow("input video", CV_WINDOW_AUTOSIZE);
	namedWindow("track mask", CV_WINDOW_AUTOSIZE);
	while (capture.read(frame)) {
		inRange(frame, Scalar(0, 127, 0), Scalar(120, 255, 120), mask); 
		// ���˶�ֵ���������ڸߵ���ֵ��Ĳ���ֱ�Ӹ�ֵΪ255���˴��������ɫ��Ĥ���ڰף�
		morphologyEx(mask, mask, MORPH_OPEN, kernel1, Point(-1, -1), 1); // ������ȥ����Ĥ�еİ�ɫ���
		dilate(mask, mask, kernel2, Point(-1, -1), 4);// ���ͣ�ʹ��ɫ���ӱ���
		imshow("track mask", mask);

		processFrame(mask, roi); // �������������λ�ñ궨
		rectangle(frame, roi, Scalar(0, 0, 255), 3, 8, 0);//BGR//���������������Ϊ��ϸ�̶ȣ��������ͣ�������С����λ
		putText(frame,"green",Point(roi.x,roi.y-20),FONT_HERSHEY_COMPLEX,1.5,Scalar(0,0,0),3,8);
		imshow("input video", frame);//rect��������˾��ε�λ�ô�С��Ϣ
		
		// Esc�˳�
		char c = waitKey(100);
		if (c == 27) {
			imwrite("1.jpg",frame);
			break;
		}
	}

	capture.release();
	waitKey(0);
	return 0;
}

void processFrame(Mat &binary, Rect &rect) {
	vector<vector<Point> > contours;
	vector<Vec4i> hireachy;
	findContours(binary, contours, hireachy, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE, Point(0, 0));//retr_externalֻ�����������������һ��ʹ����retr_tree
	//֮ǰ����ͬѧ�����й��������ȷ���İ취������Ҫͨ���ı�findContours�Ĳ�������������������������������������£�
	if (contours.size() > 0) {
		double maxArea = 0.0;
		for (size_t t = 0; t < contours.size(); t++) {
			double area = contourArea(contours[static_cast<int>(t)]);//�����t�����������
			if (area > maxArea)
			{
				maxArea = area;//����������
				rect = boundingRect(contours[static_cast<int>(t)]);
			}
		}
	}

	else {
		rect.x = rect.y = rect.width = rect.height = 0;//�������½ǵ�ĺ�������rect.x,rect.y
	}

}
