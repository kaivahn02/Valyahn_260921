import { PostForm } from "@/components/post-form";
import { createPost } from "@/lib/actions";

export default function NewPostPage() {
  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-10">
      <h1 className="mb-6 text-2xl font-bold">새 글 작성</h1>
      <PostForm action={createPost} submitLabel="등록" />
    </main>
  );
}
