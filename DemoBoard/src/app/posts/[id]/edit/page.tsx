import { notFound } from "next/navigation";
import { PostForm } from "@/components/post-form";
import { updatePost } from "@/lib/actions";
import { getPost } from "@/lib/store";

export default async function EditPostPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const post = await getPost(id);
  if (!post) {
    notFound();
  }

  const action = updatePost.bind(null, post.id);

  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-10">
      <h1 className="mb-6 text-2xl font-bold">글 수정</h1>
      <PostForm
        action={action}
        defaultTitle={post.title}
        defaultAuthor={post.author}
        defaultContent={post.content}
        submitLabel="수정 완료"
      />
    </main>
  );
}
