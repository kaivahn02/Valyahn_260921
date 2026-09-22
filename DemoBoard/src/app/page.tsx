import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { getCommentCounts, getPosts } from "@/lib/store";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;
  const [allPosts, commentCounts] = await Promise.all([
    getPosts(),
    getCommentCounts(),
  ]);

  const posts = allPosts.filter((post) =>
    q ? post.title.toLowerCase().includes(q.toLowerCase()) : true,
  );

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-10">
      <div className="mb-6 flex items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">전체 게시글</h1>
        <form className="flex gap-2">
          <Input
            name="q"
            defaultValue={q ?? ""}
            placeholder="제목 검색"
            className="w-48"
          />
          <Button type="submit" variant="secondary">
            검색
          </Button>
        </form>
      </div>

      <div className="overflow-hidden rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-16 text-center">번호</TableHead>
              <TableHead>제목</TableHead>
              <TableHead className="w-28">작성자</TableHead>
              <TableHead className="w-28">작성일</TableHead>
              <TableHead className="w-16 text-center">조회</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {posts.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="h-32 text-center text-muted-foreground"
                >
                  {q
                    ? `"${q}"에 대한 검색 결과가 없습니다.`
                    : "등록된 게시글이 없습니다."}
                </TableCell>
              </TableRow>
            ) : (
              posts.map((post, index) => (
                <TableRow key={post.id}>
                  <TableCell className="text-center text-muted-foreground">
                    {posts.length - index}
                  </TableCell>
                  <TableCell>
                    <Link
                      href={`/posts/${post.id}`}
                      className="font-medium hover:underline"
                    >
                      {post.title}
                    </Link>
                    {commentCounts.get(post.id) ? (
                      <span className="ml-2 text-xs text-muted-foreground">
                        [{commentCounts.get(post.id)}]
                      </span>
                    ) : null}
                  </TableCell>
                  <TableCell>{post.author}</TableCell>
                  <TableCell>{formatDate(post.createdAt)}</TableCell>
                  <TableCell className="text-center">{post.views}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </main>
  );
}
