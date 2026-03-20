import { useSettings } from '../queries/settings';

export default function SettingsPage() {
  useSettings();

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">الإعدادات</h1>
      <p className="text-sm text-gray-500 mb-8">إدارة قاعدة البيانات.</p>

      <div className="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center max-w-xl">
        <p className="text-4xl mb-3">📦</p>
        <h2 className="text-base font-semibold text-gray-700 mb-1">ميزة غير متوفرة</h2>
        <p className="text-sm text-gray-400">ميزة تصدير واستيراد قاعدة البيانات لم تعد متاحة.</p>
      </div>
    </div>
  );
}
