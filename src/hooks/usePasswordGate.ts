import { useState } from 'react';
import type { StoreSettings, StoreUser, SensitiveActionKey } from '../types/types';
import { shouldRequirePasswordPrompt } from '../utils/passwordGate';
import { logActivity } from '../api/activityApi';

type PendingAction = {
  actionLabel: string;
  run: () => void | Promise<void>;
};

interface UsePasswordGateArgs {
  settings: StoreSettings;
  activeUser: StoreUser | null;
}

export function usePasswordGate({ settings, activeUser }: UsePasswordGateArgs) {
  const [pending, setPending] = useState<PendingAction | null>(null);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  function clearState() {
    setPending(null);
    setPassword('');
    setError('');
  }

  function runProtected(actionKey: SensitiveActionKey, actionLabel: string, run: () => void | Promise<void>) {
    if (!shouldRequirePasswordPrompt(settings, activeUser, actionKey)) {
      run();
      return;
    }

    setPending({ actionLabel, run });
    setPassword('');
    setError('');
  }

  function confirmPassword() {
    if (!pending || !activeUser?.password) return;

    if (password !== activeUser.password) {
      setError('كلمة المرور غير صحيحة');
      if (activeUser) {
        logActivity(activeUser.id, activeUser.name, `فشل تأكيد كلمة المرور: ${pending.actionLabel}`);
      }
      return;
    }

    if (activeUser) {
      logActivity(activeUser.id, activeUser.name, `تأكيد كلمة المرور: ${pending.actionLabel}`);
    }

    const callback = pending.run;
    clearState();
    callback();
  }

  return {
    open: Boolean(pending),
    actionLabel: pending?.actionLabel || '',
    password,
    error,
    setPassword,
    close: clearState,
    confirmPassword,
    runProtected,
  };
}
