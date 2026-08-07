"use client";

import * as Dialog from "@radix-ui/react-dialog";
import { X } from "lucide-react";

export function WorkspaceDrawer({ title, triggerLabel, side, children }: { title: string; triggerLabel: string; side: "left" | "right"; children: React.ReactNode }) {
  return (
    <Dialog.Root>
      <Dialog.Trigger className="drawer-trigger button button-secondary focus-ring">{triggerLabel}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="drawer-overlay" />
        <Dialog.Content className={`drawer-content drawer-${side}`} aria-describedby={undefined}>
          <header className="drawer-header"><Dialog.Title>{title}</Dialog.Title><Dialog.Close className="icon-button focus-ring" aria-label={`关闭${title}`}><X size={20} /></Dialog.Close></header>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

