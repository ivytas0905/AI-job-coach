import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col justify-center px-6 py-16">
      <p className="mb-4 text-sm font-semibold tracking-wide text-[var(--primary)]">AI JOB COACH</p>
      <h1 className="max-w-3xl text-4xl font-semibold leading-tight sm:text-6xl">把求职经历，讲成招聘者愿意继续读的故事。</h1>
      <p className="mt-6 max-w-2xl text-lg text-[var(--ink-muted)]">在一场持续的对话里上传简历、理解职位、核对证据并生成经过你确认的定制简历。</p>
      <div className="mt-10 flex flex-wrap gap-3">
        <Link className="button button-primary focus-ring" href="/dashboard/resume/agent">开始对话</Link>
        <Link className="button button-secondary focus-ring" href="/sign-in">登录</Link>
      </div>
    </main>
  );
}
