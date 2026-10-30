-- NOT APPLIED to any remote database. Review before running.
-- Running upgrade a012reportcards -> a013threadsurface
-- Separates assistant chat history by surface. The API sets `surface` from the server-side principal, never from the client alone.

BEGIN;

ALTER TABLE public.assistant_threads ADD COLUMN surface VARCHAR(16) NOT NULL DEFAULT 'shopper';
ALTER TABLE public.assistant_threads ADD CONSTRAINT ck_assistant_threads_surface CHECK (surface IN ('shopper','merchant'));
CREATE INDEX ix_assistant_threads_owner_surface ON public.assistant_threads (owner_subject, surface, updated_at);

COMMIT;
