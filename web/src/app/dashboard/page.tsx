import React from 'react'
import { currentUser } from "@clerk/nextjs/server"

export default async function Dashboard() {
  const user = await currentUser()
  return (
    <main className="p-10">
      <h1 className="text-3xl font-bold">Hello Dashboard</h1>
      <p className="mt-2 text-gray-600">Welcome, {user?.firstName || "friend"}.</p>
    </main>
  )
}
