<h1 align="center"> 인천대학교 2023 캡스톤디자인 Golden_Time팀 </h1> <br>
<h2 align="center"> 실시간 위협행동 감지 시스템 </h2> <br>

### Built With


* [![Swift][Swift]][Swift-url]
* [![AWS][AWS]][AWS-url]

*[![Xcode](https://img.shields.io/badge/Xcode-007ACC?style=for-the-badge&logo=Xcode&logoColor=white)]
* [![Vue][Vue.js]][Vue-url]
* [![Angular][Angular.io]][Angular-url]
* [![Svelte][Svelte.dev]][Svelte-url]
* [![Laravel][Laravel.com]][Laravel-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![JQuery][JQuery.com]][JQuery-url]


## Contributors

* 정종원 - jjwon2149@gmail.com <br>
https://simth999wrld.tistory.com

* 신상우 - 입력바람
* 이재혁 - 입력바람

## Features 

서버
* 서버는 AWS EC2 g4dn인스턴스(GPU포함)에서 Ubuntu 18.04 환경에서 실행.

* Flask 웹 프레임워크와 OpenCV 라이브러리를 사용하여 라이브 비디오 피드가 있는 실시간 객체 감지 애플리케이션을 만드는 Python 스크립트입니다. 스크립트는 소켓을 사용하여 클라이언트 연결을 수신하고 바이트 스트림 형식으로 비디오 프레임을 수신합니다. 그런 다음 OpenCV를 사용하여 바이트 스트림을 디코딩하고 사전 훈련된 YOLOv4 딥 러닝 모델을 사용하여 비디오 프레임에서 객체 감지를 수행합니다. 감지된 개체는 경계 상자와 클래스 레이블로 강조 표시됩니다.

* 비디오 프레임은 애플리케이션의 성능을 향상시키는 데 도움이 되는 멀티스레딩을 사용하여 처리됩니다. VideoStreamingThread 클래스는 비디오 프레임을 입력으로 사용하고 YOLOv3 모델을 사용하여 객체 감지를 수행하고 처리된 프레임을 반환하는 스레드를 정의합니다. 생성 기능은 비디오 스트리밍 스레드를 실행하고 클라이언트에서 비디오 프레임을 수신합니다. 그런 다음 처리된 프레임을 멀티파트 HTTP 응답의 형태로 클라이언트에 다시 보냅니다.

* 이 스크립트는 cv2.dnn.readNet, cv2.dnn.blobFromImage, cv2.dnn.NMSBoxes, cv2.rectangle 및 cv2.putText를 비롯한 여러 OpenCV 함수를 사용하여 개체 감지를 수행하고 감지된 개체 주위에 경계 상자를 그립니다. 객체 감지에 사용되는 YOLOv4 모델은 사전 훈련된 가중치 파일및 구성 파일에서 로드됩니다. 감지된 개체의 클래스 레이블은 텍스트 파일에서 로드됩니다.

앱
* 라즈베리 파이 카메라(CCTV)화면 실시간 스트리밍
* 위협 발생시 알림
* 긴급 신고 기능
* 폭력 영상 재확인 가능

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

<!--
<img src="https://img.shields.io/badge/텍스트-컬러코드?style=원하는스타일&logo=아이콘이름&logoColor=white"/>

https://github.com/Ileriayo/markdown-badges

-->

[Swift]: https://img.shields.io/badge/Swift-F05138?style=for-the-badge&logo=Swift&logoColor=white
[Swift-url]: https://developer.apple.com/
[AWS]: https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white
[AWS-url]: https://aws.amazon.com/

[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
