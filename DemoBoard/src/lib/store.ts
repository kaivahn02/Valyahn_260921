import { supabase } from "./supabase";
import type { Comment, Post } from "./types";

type PostRow = {
  id: string;
  title: string;
  author: string;
  content: string;
  views: number;
  created_at: string;
  updated_at: string;
};

type CommentRow = {
  id: string;
  post_id: string;
  author: string;
  content: string;
  created_at: string;
};

function toPost(row: PostRow): Post {
  return {
    id: row.id,
    title: row.title,
    author: row.author,
    content: row.content,
    views: row.views,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

function toComment(row: CommentRow): Comment {
  return {
    id: row.id,
    postId: row.post_id,
    author: row.author,
    content: row.content,
    createdAt: row.created_at,
  };
}

export async function getPosts(): Promise<Post[]> {
  const { data, error } = await supabase
    .from("posts")
    .select("*")
    .order("created_at", { ascending: false });
  if (error) throw new Error(error.message);
  return data.map(toPost);
}

export async function getPost(id: string): Promise<Post | null> {
  const { data, error } = await supabase
    .from("posts")
    .select("*")
    .eq("id", id)
    .maybeSingle();
  if (error) throw new Error(error.message);
  return data ? toPost(data) : null;
}

export async function getCommentCounts(): Promise<Map<string, number>> {
  const { data, error } = await supabase.from("comments").select("post_id");
  if (error) throw new Error(error.message);

  const counts = new Map<string, number>();
  for (const row of data as Pick<CommentRow, "post_id">[]) {
    counts.set(row.post_id, (counts.get(row.post_id) ?? 0) + 1);
  }
  return counts;
}

export async function getComments(postId: string): Promise<Comment[]> {
  const { data, error } = await supabase
    .from("comments")
    .select("*")
    .eq("post_id", postId)
    .order("created_at", { ascending: true });
  if (error) throw new Error(error.message);
  return data.map(toComment);
}

export async function createPost(input: {
  title: string;
  author: string;
  content: string;
}): Promise<Post> {
  const { data, error } = await supabase
    .from("posts")
    .insert(input)
    .select()
    .single();
  if (error) throw new Error(error.message);
  return toPost(data);
}

export async function updatePost(
  id: string,
  input: { title: string; author: string; content: string },
): Promise<Post> {
  const { data, error } = await supabase
    .from("posts")
    .update({ ...input, updated_at: new Date().toISOString() })
    .eq("id", id)
    .select()
    .maybeSingle();
  if (error) throw new Error(error.message);
  if (!data) throw new Error("게시글을 찾을 수 없습니다.");
  return toPost(data);
}

export async function deletePost(id: string): Promise<void> {
  const { error } = await supabase.from("posts").delete().eq("id", id);
  if (error) throw new Error(error.message);
}

export async function incrementViews(id: string): Promise<void> {
  const { error } = await supabase.rpc("increment_post_views", {
    post_id: id,
  });
  if (error) throw new Error(error.message);
}

export async function addComment(
  postId: string,
  input: { author: string; content: string },
): Promise<Comment> {
  const { data, error } = await supabase
    .from("comments")
    .insert({ post_id: postId, ...input })
    .select()
    .single();
  if (error) throw new Error(error.message);
  return toComment(data);
}

export async function deleteComment(commentId: string): Promise<void> {
  const { error } = await supabase
    .from("comments")
    .delete()
    .eq("id", commentId);
  if (error) throw new Error(error.message);
}
