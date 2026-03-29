import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useProducts, useCreateProduct, useUpdateProduct, useDeleteProduct } from '../queries/products';
import { useCategories, useCreateCategory, useDeleteCategory } from '../queries/categories';
import { formatCurrency } from '../utils/formatters';
import { ApiError } from '../api/client';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import EmptyState from '../components/EmptyState';
import type { Product } from '../types/types';

interface ProductFormData {
  name: string;
  price: number;
  categoryId: string | null;
  sizes: { id: string; name: string; price: number; sortOrder: number }[];
}

export default function ProductsPage() {
  const { data: products = [], isLoading: productsLoading } = useProducts();
  const { data: categories = [], isLoading: categoriesLoading } = useCategories();

  const createProduct = useCreateProduct();
  const updateProduct = useUpdateProduct();
  const deleteProduct = useDeleteProduct();
  const createCategory = useCreateCategory();
  const deleteCategory = useDeleteCategory();

  const [search, setSearch] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Product | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Product | null>(null);
  const [deleteCatTarget, setDeleteCatTarget] = useState<{ id: string; name: string } | null>(null);
  const [catError, setCatError] = useState('');

  const [newCatName, setNewCatName] = useState('');

  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [sizes, setSizes] = useState<{ name: string; price: number }[]>([]);
  const [error, setError] = useState('');

  const filtered = products.filter((p) => {
    const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = filterCategory === 'all' || p.categoryId === filterCategory;
    return matchesSearch && matchesCategory;
  });

  function openAdd() {
    setEditing(null);
    setName('');
    setPrice('');
    setCategoryId('');
    setSizes([]);
    setError('');
    setModalOpen(true);
  }

  function openEdit(product: Product) {
    setEditing(product);
    setName(product.name);
    setPrice(String(product.price));
    setCategoryId(product.categoryId || '');
    setSizes((product.sizes || []) as { name: string; price: number }[]);
    setError('');
    setModalOpen(true);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) {
      setError('اسم المنتج مطلوب.');
      return;
    }
    const p = parseFloat(price);
    if (isNaN(p) || p <= 0) {
      setError('السعر يجب أن يكون رقماً موجباً.');
      return;
    }

    if (sizes.length > 0) {
      for (const size of sizes) {
        if (!size.name.trim() || size.price <= 0) {
          setError('يجب إدخال اسم وسعر صحيح لكل حجم.');
          return;
        }
      }
    }

    const productData: ProductFormData = {
      name: name.trim(),
      price: p,
      categoryId: categoryId || null,
      sizes: sizes.map((s, i) => ({
        id: crypto.randomUUID(),
        name: s.name,
        price: s.price,
        sortOrder: i,
      })),
    };

    if (editing) {
      updateProduct.mutate(
        { id: editing.id, data: { ...productData, categoryId: productData.categoryId || undefined } },
        {
          onSuccess: () => setModalOpen(false),
          onError: (err) => {
            if (err instanceof ApiError) {
              setError(err.message || 'فشل تحديث المنتج.');
              return;
            }
            setError('فشل تحديث المنتج.');
          },
        }
      );
    } else {
      const createdAt = new Date().toISOString();
      createProduct.mutate(
        {
          id: crypto.randomUUID(),
          createdAt,
          ...productData,
          categoryId: productData.categoryId || undefined,
        },
        {
          onSuccess: () => setModalOpen(false),
          onError: (err) => {
            if (err instanceof ApiError) {
              setError(err.message || 'فشل إنشاء المنتج.');
              return;
            }
            setError('فشل إنشاء المنتج.');
          },
        }
      );
    }
  }

  function handleDelete() {
    if (deleteTarget) {
      deleteProduct.mutate(deleteTarget.id, { onSuccess: () => setDeleteTarget(null) });
    }
  }

  function handleAddCategory() {
    if (newCatName.trim()) {
      createCategory.mutate(
        { id: crypto.randomUUID(), name: newCatName.trim() },
        { onSuccess: () => setNewCatName('') }
      );
    }
  }

  if (productsLoading || categoriesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-violet-200 border-t-violet-600 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">المنتجات</h1>
          <p className="text-sm text-gray-500 mt-1">{products.length} منتج في الكتالوج</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={openAdd}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-violet-600 text-white text-sm font-medium rounded-xl hover:bg-violet-700 transition-colors shadow-lg shadow-violet-200"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            إضافة منتج
          </button>
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">التصنيفات</h2>
        <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex flex-wrap gap-2 mb-4">
            {categories.map((cat) => (
              <div key={cat.id} className="flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-lg border border-gray-200 text-sm group">
                <span className="font-medium text-gray-700">{cat.name}</span>
                <button
                  onClick={() => setDeleteCatTarget({ id: cat.id, name: cat.name })}
                  className="w-5 h-5 flex items-center justify-center text-gray-400 hover:text-red-500 rounded-full hover:bg-red-50 transition-colors"
                >
                  ×
                </button>
              </div>
            ))}
            {categories.length === 0 && <p className="text-sm text-gray-400 italic py-1">لا توجد تصنيفات حالياً</p>}
          </div>
          <div className="flex gap-2 max-w-sm">
            <input
              type="text"
              placeholder="اسم تصنيف جديد..."
              value={newCatName}
              onChange={(e) => setNewCatName(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleAddCategory();
                }
              }}
            />
            <button
              onClick={handleAddCategory}
              disabled={createCategory.isPending}
              className="px-3 py-2 bg-stone-800 text-white text-sm font-medium rounded-xl hover:bg-stone-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createCategory.isPending ? '...' : 'إضافة'}
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <svg className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="بحث عن المنتجات..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pr-10 pl-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
          />
        </div>
        <div className="sm:w-48">
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="w-full px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
          >
            <option value="all">كل التصنيفات</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon="📦"
          title={search ? 'لا توجد منتجات مطابقة' : 'لا توجد منتجات بعد'}
          description={search ? 'جرب مصطلح بحث آخر' : 'أضف أول منتج للبدء'}
          action={!search ? { label: 'إضافة منتج', onClick: openAdd } : undefined}
        />
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-right px-6 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">المنتج</th>
                  <th className="text-right px-6 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">السعر</th>
                  <th className="text-left px-6 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">إجراءات</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.map((product) => (
                  <tr key={product.id} className="group hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4">
                      <p className="font-medium text-gray-900">{product.name}</p>
                      {product.categoryId && (
                        <span className="inline-block mt-1 text-xs px-2 py-0.5 bg-gray-100 text-gray-500 rounded-md">
                          {(product as { category_name?: string }).category_name || categories.find(c => c.id === product.categoryId)?.name || 'تصنيف محذوف'}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 font-semibold text-gray-900">{formatCurrency(product.price)}</td>
                    <td className="px-6 py-4 text-left">
                      <div className="flex items-center justify-start gap-1">
                        <Link
                          to={`/new-order?product=${encodeURIComponent(product.name)}`}
                          className="hidden group-hover:inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-violet-700 bg-violet-50 hover:bg-violet-100 rounded-lg transition-colors border border-violet-100"
                          title="بدء طلب بهذا المنتج"
                        >
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                          بيع
                        </Link>
                        <button
                          onClick={() => openEdit(product as Product)}
                          disabled={updateProduct.isPending}
                          className="p-2 text-gray-400 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          title="تعديل"
                        >
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => setDeleteTarget(product as Product)}
                          disabled={deleteProduct.isPending}
                          className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          title="حذف"
                        >
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'تعديل المنتج' : 'إضافة منتج'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="px-4 py-2 bg-red-50 text-red-600 rounded-lg text-sm">{error}</div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">الاسم *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
              placeholder="اسم المنتج"
              autoFocus
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">التصنيف</label>
            <select
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
            >
              <option value="">بدون تصنيف</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">السعر *</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
              placeholder="0.00"
            />
          </div>

          <div className="pt-2 border-t border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">الأحجام (اختياري)</label>
              <button
                type="button"
                onClick={() => setSizes([...sizes, { name: '', price: 0 }])}
                className="text-xs text-violet-600 hover:text-violet-700 font-medium flex items-center gap-1"
              >
                + إضافة حجم
              </button>
            </div>
            
            <div className="space-y-2">
              {sizes.map((size, idx) => (
                <div key={idx} className="flex gap-2">
                  <input
                    type="text"
                    placeholder="الحجم (مثلاً: كبير)"
                    value={size.name}
                    onChange={(e) => {
                      const newSizes = [...sizes];
                      newSizes[idx].name = e.target.value;
                      setSizes(newSizes);
                    }}
                    className="flex-1 px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    placeholder="السعر"
                    value={size.price || ''}
                    onChange={(e) => {
                      const newSizes = [...sizes];
                      newSizes[idx].price = parseFloat(e.target.value) || 0;
                      setSizes(newSizes);
                    }}
                    className="w-24 px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                  <button
                    type="button"
                    onClick={() => setSizes(sizes.filter((_, i) => i !== idx))}
                    className="w-8 h-8 flex items-center justify-center text-red-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    ×
                  </button>
                </div>
              ))}
              {sizes.length === 0 && (
                <p className="text-xs text-gray-400 italic">لا توجد أحجام مضافة لهذا المنتج.</p>
              )}
            </div>
          </div>

          <div className="pt-2 border-t border-gray-100" />
          <div className="flex gap-3 justify-start pt-2">
            <button
              type="button"
              onClick={() => setModalOpen(false)}
              className="px-4 py-2.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-xl hover:bg-gray-200 transition-colors"
            >
              إلغاء
            </button>
            <button
              type="submit"
              disabled={createProduct.isPending || updateProduct.isPending}
              className="px-4 py-2.5 text-sm font-medium text-white bg-violet-600 rounded-xl hover:bg-violet-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {editing ? (updateProduct.isPending ? '...' : 'تحديث') : (createProduct.isPending ? '...' : 'إضافة منتج')}
            </button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="حذف المنتج"
        message={`هل أنت متأكد من حذف "${deleteTarget?.name}"؟ لا يمكن التراجع عن هذا الإجراء.`}
        confirmLabel="حذف"
        danger
      />

      <ConfirmDialog
        open={!!deleteCatTarget}
        onClose={() => setDeleteCatTarget(null)}
        onConfirm={() => {
          if (deleteCatTarget) {
            deleteCategory.mutate(deleteCatTarget.id, {
              onError: () => {
                setCatError('لا يمكن حذف هذا التصنيف لأنه مرتبط بمنتجات.');
                setTimeout(() => setCatError(''), 4000);
              },
              onSuccess: () => setDeleteCatTarget(null),
            });
          }
        }}
        title="حذف التصنيف"
        message={`هل أنت متأكد من حذف التصنيف "${deleteCatTarget?.name}"؟`}
        confirmLabel="حذف"
        danger
      />

      {catError && (
        <div className="fixed bottom-4 right-4 z-50 px-4 py-3 bg-red-50 text-red-700 rounded-xl text-sm font-medium shadow-lg border border-red-200 animate-fade-in flex items-center gap-2">
          <svg className="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {catError}
        </div>
      )}
    </div>
  );
}
