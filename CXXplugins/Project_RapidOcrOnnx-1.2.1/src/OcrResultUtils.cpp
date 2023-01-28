#ifdef __JNI__
#include <OcrUtils.h>
#include "OcrResultUtils.h"

OcrResultUtils::OcrResultUtils(JNIEnv *env, OcrResult &ocrResult) {
    jniEnv = env;

    jclass jOcrResultClass = env->FindClass("com/benjaminwan/ocrlibrary/OcrResult");

    if (jOcrResultClass == NULL) {
        printf("OcrResult class is null\n");
    }

    jmethodID jOcrResultConstructor = env->GetMethodID(jOcrResultClass, "<init>",
                                                       "(DLjava/util/ArrayList;DLjava/lang/String;)V");

    jobject textBlocks = getTextBlocks(ocrResult.textBlocks);
    jdouble dbNetTime = (jdouble) ocrResult.dbNetTime;
    jdouble detectTime = (jdouble) ocrResult.detectTime;
    jstring jStrRest = jniEnv->NewStringUTF(ocrResult.strRes.c_str());

    jOcrResult = env->NewObject(jOcrResultClass, jOcrResultConstructor, dbNetTime,
                                textBlocks, detectTime, jStrRest);
}

OcrResultUtils::~OcrResultUtils() {
    jniEnv = NULL;
}

jobject OcrResultUtils::getJObject() {
    return jOcrResult;
}

jclass OcrResultUtils::newJListClass() {
    jclass clazz = jniEnv->FindClass("java/util/ArrayList");
    if (clazz == NULL) {
        printf("ArrayList class is null\n");
        return NULL;
    }
    return clazz;
}

jmethodID OcrResultUtils::getListConstructor(jclass clazz) {
    jmethodID constructor = jniEnv->GetMethodID(clazz, "<init>", "()V");
    return constructor;
}

jobject OcrResultUtils::newJPoint(cv::Point &point) {
    jclass clazz = jniEnv->FindClass("com/benjaminwan/ocrlibrary/Point");
    if (clazz == NULL) {
        printf("Point class is null\n");
        return NULL;
    }
    jmethodID constructor = jniEnv->GetMethodID(clazz, "<init>", "(II)V");
    jobject obj = jniEnv->NewObject(clazz, constructor, point.x, point.y);
    return obj;
}

jobject OcrResultUtils::newJBoxPoint(std::vector<cv::Point> &boxPoint) {
    jclass jListClass = newJListClass();
    jmethodID jListConstructor = getListConstructor(jListClass);
    jobject jList = jniEnv->NewObject(jListClass, jListConstructor);
    jmethodID jListAdd = jniEnv->GetMethodID(jListClass, "add", "(Ljava/lang/Object;)Z");

    for (auto point : boxPoint) {
        jobject jPoint = newJPoint(point);
        jniEnv->CallBooleanMethod(jList, jListAdd, jPoint);
    }
    return jList;
}

jobject OcrResultUtils::getTextBlock(TextBlock &textBlock) {
    jobject jBoxPint = newJBoxPoint(textBlock.boxPoint);
    jfloat jBoxScore = (jfloat) textBlock.boxScore;
    jfloat jAngleScore = (jfloat) textBlock.angleScore;
    jdouble jAngleTime = (jdouble) textBlock.angleTime;
    jstring jText = jniEnv->NewStringUTF(textBlock.text.c_str());
    jobject jCharScores = newJScoreArray(textBlock.charScores);
    jdouble jCrnnTime = (jdouble) textBlock.crnnTime;
    jdouble jBlockTime = (jdouble) textBlock.blockTime;
    jclass clazz = jniEnv->FindClass("com/benjaminwan/ocrlibrary/TextBlock");
    if (clazz == NULL) {
        printf("TextBlock class is null\n");
        return NULL;
    }
    jmethodID constructor = jniEnv->GetMethodID(clazz, "<init>",
                                                "(Ljava/util/ArrayList;FIFDLjava/lang/String;[FDD)V");
    jobject obj = jniEnv->NewObject(clazz, constructor, jBoxPint, jBoxScore, textBlock.angleIndex,
                                    jAngleScore, jAngleTime, jText, jCharScores, jCrnnTime,
                                    jBlockTime);
    return obj;
}

jobject OcrResultUtils::getTextBlocks(std::vector<TextBlock> &textBlocks) {
    jclass jListClass = newJListClass();
    jmethodID jListConstructor = getListConstructor(jListClass);
    jobject jList = jniEnv->NewObject(jListClass, jListConstructor);
    jmethodID jListAdd = jniEnv->GetMethodID(jListClass, "add", "(Ljava/lang/Object;)Z");

    for (int i = 0; i < textBlocks.size(); ++i) {
        auto textBlock = textBlocks[i];
        jobject jTextBlock = getTextBlock(textBlock);
        jniEnv->CallBooleanMethod(jList, jListAdd, jTextBlock);
    }
    return jList;
}

jfloatArray OcrResultUtils::newJScoreArray(std::vector<float> &scores) {
    jfloatArray jScores = jniEnv->NewFloatArray(scores.size());
    jniEnv->SetFloatArrayRegion(jScores, 0, scores.size(), (jfloat *) scores.data());
    return jScores;
}

#endif