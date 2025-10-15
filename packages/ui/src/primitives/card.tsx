import type { PropsWithChildren, ReactNode } from 'react';
import { clsx } from 'clsx';

export interface CardProps extends PropsWithChildren {
  title?: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  className?: string;
}

export const Card = ({ title, description, actions, className, children }: CardProps) => {
  return (
    <section
      className={clsx(
        'rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm shadow-slate-950/40',
        className
      )}
    >
      {(title || description || actions) && (
        <header className="mb-4 flex items-start justify-between gap-4">
          <div>
            {title ? <h3 className="text-lg font-semibold text-white">{title}</h3> : null}
            {description ? <p className="text-sm text-slate-400">{description}</p> : null}
          </div>
          {actions}
        </header>
      )}
      {children}
    </section>
  );
};
