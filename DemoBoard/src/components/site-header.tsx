import Link from "next/link";
import { Button } from "@/components/ui/button";

export function SiteHeader() {
  return (
    <header className="border-b">
      <div className="mx-auto flex w-full max-w-4xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-lg font-bold tracking-tight">
          DemoBoard
        </Link>
        <Button render={<Link href="/posts/new" />} nativeButton={false} size="sm">
          글쓰기
        </Button>
      </div>
    </header>
  );
}
