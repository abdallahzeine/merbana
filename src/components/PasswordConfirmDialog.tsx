import Modal from './Modal';

interface PasswordConfirmDialogProps {
  open: boolean;
  actionLabel: string;
  password: string;
  error: string;
  onPasswordChange: (value: string) => void;
  onClose: () => void;
  onConfirm: () => void;
}

export default function PasswordConfirmDialog({
  open,
  actionLabel,
  password,
  error,
  onPasswordChange,
  onClose,
  onConfirm,
}: PasswordConfirmDialogProps) {
  return (
    <Modal open={open} onClose={onClose} title="تأكيد كلمة المرور" width="max-w-sm">
      <div className="space-y-4">
        <p className="text-sm text-gray-600">
          يرجى إدخال كلمة المرور لتنفيذ: <span className="font-semibold text-gray-900">{actionLabel}</span>
        </p>
        {error && (
          <div className="px-3 py-2 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
            {error}
          </div>
        )}
        <input
          type="password"
          value={password}
          onChange={(e) => onPasswordChange(e.target.value)}
          className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
          placeholder="كلمة المرور"
          autoFocus
        />
        <div className="flex items-center justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            إلغاء
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700 transition-colors"
          >
            تأكيد
          </button>
        </div>
      </div>
    </Modal>
  );
}
