import { NavLink } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useSettings } from '../queries/settings';
import { useProducts } from '../queries/products';
import { useDebtors } from '../queries/debtors';

export default function Sidebar() {
  const [open, setOpen] = useState(false);
  const { activeUser, logout } = useAuth();
  const settingsQuery = useSettings();
  const productsQuery = useProducts();
  const debtorsQuery = useDebtors();

  const products = productsQuery.data ?? [];
  const debtors = debtorsQuery.data ?? [];
  const settings = settingsQuery.data;

  const unpaidDebtorCount = debtors.filter(d => !d.paidAt).length;

  useEffect(() => {
    function handleResize() {
      if (window.innerWidth >= 1024) setOpen(false);
    }
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const NAV_ITEMS = [
    { to: '/', label: 'الرئيسية', icon: '🏠', badge: 0 },
    { to: '/products', label: 'المنتجات', icon: '📦', badge: 0 },
    { to: '/new-order', label: 'طلب جديد', icon: '🛒', badge: 0 },
    { to: '/orders', label: 'الطلبات', icon: '📋', badge: 0 },
    { to: '/register', label: 'الصندوق', icon: '💵', badge: 0 },
    { to: '/debtors', label: 'الديون', icon: '💳', badge: unpaidDebtorCount },
    { to: '/reports', label: 'التقارير', icon: '📊', badge: 0 },
    { to: '/settings', label: 'الإعدادات', icon: '⚙️', badge: 0 },
  ];

  return (
    <>
      <button
        className="fixed top-3 right-3 z-50 lg:hidden bg-white/90 backdrop-blur-sm text-stone-700 p-2.5 rounded-xl shadow-md border border-stone-200 active:scale-95 transition-transform"
        onClick={() => setOpen(!open)}
        aria-label="القائمة"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          {open ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {open && (
        <div className="fixed inset-0 bg-stone-900/30 backdrop-blur-sm z-30 lg:hidden" onClick={() => setOpen(false)} />
      )}

      <aside
        className={`
          fixed inset-y-0 right-0 z-40 w-64 bg-white border-l border-stone-200 text-stone-800 flex flex-col shadow-xl
          transform transition-transform duration-300 ease-in-out
          lg:sticky lg:top-0 lg:h-screen lg:shrink-0 lg:w-72 lg:translate-x-0 lg:shadow-none xl:w-80 print:hidden
          ${open ? 'translate-x-0' : 'translate-x-full'}
        `}
      >
        <div className="px-6 py-5 border-b border-stone-100">
          <h1 className="text-xl font-bold tracking-tight bg-linear-to-r from-violet-600 to-amber-500 bg-clip-text text-transparent">
            {settings?.companyName ?? '...'}
          </h1>
          <p className="text-xs text-stone-400 mt-1">نظام إدارة المتجر</p>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-violet-50 text-violet-700 shadow-sm ring-1 ring-violet-100'
                    : 'text-stone-500 hover:bg-stone-50 hover:text-stone-800'
                }`
              }
            >
              <span className="text-lg">{item.icon}</span>
              <span className="flex-1">{item.label}</span>
              {item.badge > 0 && (
                <span className="min-w-5 h-5 px-1.5 bg-amber-500 text-white text-xs font-bold rounded-full flex items-center justify-center leading-none">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-stone-100">
          {activeUser && (
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-violet-100 text-violet-700 rounded-lg flex items-center justify-center text-xs font-bold shrink-0">
                {activeUser.name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-stone-800 truncate">{activeUser.name}</p>
              </div>
              <button
                onClick={logout}
                className="p-1.5 text-stone-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                title="تبديل المستخدم"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          )}
          <p className="text-xs text-stone-300">© 2026 {settings?.companyName ?? '...'}</p>
        </div>
      </aside>
    </>
  );
}
