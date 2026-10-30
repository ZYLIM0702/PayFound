export function safeNext(value: string | null): string {
  if (!value || !value.startsWith('/') || value.startsWith('//') || value.includes('\\')) return '/';
  // WHATWG URL parsing removes tabs/newlines before identifying an authority.
  // Reject controls before a nominally relative path can become //another-host.
  if (Array.from(value).some(character => character.charCodeAt(0) < 32 || character.charCodeAt(0) === 127)) return '/';
  return value;
}

export function invitationSessionFromHash(hash: string): { access_token: string; refresh_token: string } | null {
  const params = new URLSearchParams(hash.replace(/^#/, ''));
  const access = params.get('access_token');
  const refresh = params.get('refresh_token');
  return params.get('type') === 'invite' && access && refresh ? { access_token: access, refresh_token: refresh } : null;
}
