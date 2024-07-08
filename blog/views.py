from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post
from .serializers import PostSerializer
from .s3_utils import upload_file_to_s3

class PostView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        post_id = kwargs.get('id')
        if post_id:
            post = Post.objects.filter(id=post_id, is_deleted=False).first()
            if post:
                serializer = PostSerializer(post)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        posts = Post.objects.filter(is_deleted=False)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        post_id = kwargs.get('id')
        post = Post.objects.filter(id=post_id, is_deleted=False).first()
        if not post:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        post_id = kwargs.get('id')
        post = Post.objects.filter(id=post_id, is_deleted=False).first()
        if not post:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        post.is_deleted = True
        post.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ImageView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '업로드할 파일이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        key = f"images/{file.name}"
        ExtraArgs = {
            'ContentType': file.content_type
        }
        img_url = upload_file_to_s3(file, key, ExtraArgs)
        if not img_url:
            return Response({"message": "S3 버킷에 파일 업로드 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"image_url": img_url}, status=status.HTTP_200_OK)
