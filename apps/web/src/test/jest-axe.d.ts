declare module "jest-axe" {
  interface AxeResult { violations: unknown[] }
  export function axe(element: Element): Promise<AxeResult>;
}
