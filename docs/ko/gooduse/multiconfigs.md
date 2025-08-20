# 여러 구성 파일 생성

이전에는 소프트웨어를 서로 다른 구성으로 동시에 열려면 소프트웨어 전체를 복제하는 수밖에 없어 많은 공간이 낭비되었습니다.

최근 이 기능이 최적화되어 소프트웨어가 지정된 디렉터리의 구성 파일을 읽을 수 있게 되었습니다. 이제 런타임에 사용할 구성 파일 디렉터리를 지정하기만 하면 다른 구성 파일을 사용할 수 있습니다.

방법은 다음과 같습니다:

1. 메인 프로그램의 바로 가기 생성

    ![img](https://image.lunatranslator.org/zh/multiconfigs.png)

1. 바로 가기의 속성 -> 대상 수정, 끝에 ` --userconfig=XXXX` 추가. `XXXX`를 새로운 구성으로 사용할 폴더 이름으로 바꾸세요. 그런 다음 이 바로 가기로 소프트웨어를 실행합니다.

    `XXXX`가 존재하지 않는 폴더인 경우 기본 설정으로 소프트웨어가 시작되고 이 폴더가 생성됩니다.

    `XXXX`가 기존 폴더인 경우 이 폴더의 구성 파일을 사용해 소프트웨어가 실행됩니다. 기존 userconfig 폴더를 복사하고 `XXXX`를 복사한 폴더 이름으로 지정하면 이전 구성에서 새로운 구성으로 분기할 수 있습니다.

    ![img](https://image.lunatranslator.org/zh/multiconfigs2.png)

    ![img](https://image.lunatranslator.org/zh/multiconfigs3.png)