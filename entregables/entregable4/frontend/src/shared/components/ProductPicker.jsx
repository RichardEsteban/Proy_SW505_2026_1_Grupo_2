import { useMemo, useState } from 'react'
import Button from '@/shared/components/Button'
import Input from '@/shared/components/Input'
import Select from '@/shared/components/Select'
import { formatMoney } from '@/shared/utils/formatMoney'

function normalizeText(value) {
  return String(value ?? '').trim()
}

function numberValue(value) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

function getProductId(product) {
  return product.idProducto ?? product.id ?? product.productoId
}

function getProductName(product) {
  return product.nombreProducto ?? product.producto ?? product.nombre ?? 'Producto sin nombre'
}

function getProductCode(product) {
  return product.codigoBarras ?? product.codigo ?? product.sku ?? ''
}

function getProductCategory(product) {
  return product.categoria ?? product.nombreCategoria ?? product.categoriaNombre ?? 'Sin categoría'
}

function getProductPrice(product) {
  return numberValue(product.precioVenta ?? product.precioUnitario ?? product.precio ?? product.precioCompraUnitario)
}

function getProductIgv(product) {
  return numberValue(product.porcentajeIgv ?? product.igv ?? 18)
}

function getProductStock(product) {
  if (product.stockDisponible === undefined && product.stock === undefined) return null
  return numberValue(product.stockDisponible ?? product.stock)
}

function getProductStockMin(product) {
  if (product.stockMinimo === undefined && product.stockMin === undefined) return null
  return numberValue(product.stockMinimo ?? product.stockMin)
}

function lineTotal({ product, quantity, priceField, selectedPrice }) {
  const unitPrice = priceField ? numberValue(selectedPrice) : getProductPrice(product)
  return unitPrice * numberValue(quantity)
}

function getDefaultDraft(product, priceField) {
  return {
    quantity: 1,
    price: priceField ? normalizeText(product.precioCompraUnitario ?? product.precioCompra ?? product.costoCompra ?? '') : ''
  }
}

export default function ProductPicker({
  products = [],
  selectedItems = [],
  onChange,
  title = 'Buscar productos',
  description = 'Busca por nombre o código, filtra por categoría y agrega productos al detalle.',
  quantityField = 'cantidad',
  priceField = null,
  priceLabel = 'Precio',
  selectedTitle = 'Productos seleccionados',
  addButtonLabel = 'Agregar',
  showStock = false,
  showStockMin = false,
  showUnitPrice = false,
  showLineTotal = false,
  lowStockFirst = false,
  requireAvailableStock = false,
  stockLabel = 'Stock',
  quantityLabel = 'Cantidad',
  searchPlaceholder = 'Buscar por nombre o código',
  emptyMessage = 'No hay productos para mostrar.',
  selectedEmptyMessage = 'Todavía no agregaste productos.',
  maxVisibleProducts = 80
}) {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [draftById, setDraftById] = useState({})

  const normalizedProducts = useMemo(() => products.map((product) => {
    const id = String(getProductId(product) ?? '')
    return {
      raw: product,
      id,
      name: getProductName(product),
      code: getProductCode(product),
      category: getProductCategory(product),
      price: getProductPrice(product),
      igv: getProductIgv(product),
      stock: getProductStock(product),
      stockMin: getProductStockMin(product)
    }
  }).filter((product) => product.id), [products])

  const selectedIds = useMemo(() => new Set(selectedItems.map((item) => String(item.idProducto))), [selectedItems])

  const categories = useMemo(() => {
    const unique = new Set(normalizedProducts.map((product) => product.category || 'Sin categoría'))
    return Array.from(unique).sort((a, b) => a.localeCompare(b))
  }, [normalizedProducts])

  const filteredProducts = useMemo(() => {
    const term = search.trim().toLowerCase()

    const filtered = normalizedProducts.filter((product) => {
      const matchesSearch = !term || product.name.toLowerCase().includes(term) || product.code.toLowerCase().includes(term)
      const matchesCategory = !category || product.category === category
      return matchesSearch && matchesCategory
    })

    if (lowStockFirst) {
      filtered.sort((a, b) => {
        const aRatio = a.stockMin ? a.stock / a.stockMin : Number.MAX_SAFE_INTEGER
        const bRatio = b.stockMin ? b.stock / b.stockMin : Number.MAX_SAFE_INTEGER
        return aRatio - bRatio || a.name.localeCompare(b.name)
      })
    } else {
      filtered.sort((a, b) => a.name.localeCompare(b.name))
    }

    return filtered.slice(0, maxVisibleProducts)
  }, [category, lowStockFirst, maxVisibleProducts, normalizedProducts, search])

  const productById = useMemo(() => {
    const map = new Map()
    normalizedProducts.forEach((product) => map.set(product.id, product))
    return map
  }, [normalizedProducts])

  function getDraft(product) {
    return draftById[product.id] || getDefaultDraft(product.raw, priceField)
  }

  function updateDraft(productId, field, value) {
    setDraftById((current) => ({
      ...current,
      [productId]: {
        ...(current[productId] || { quantity: 1, price: '' }),
        [field]: value
      }
    }))
  }

  function addProduct(product) {
    const draft = getDraft(product)
    const quantity = Math.max(1, numberValue(draft.quantity))
    const existingIndex = selectedItems.findIndex((item) => String(item.idProducto) === product.id)

    if (existingIndex >= 0) {
      const updated = selectedItems.map((item, index) => {
        if (index !== existingIndex) return item
        return {
          ...item,
          [quantityField]: numberValue(item[quantityField]) + quantity,
          ...(priceField ? { [priceField]: draft.price } : {})
        }
      })
      onChange(updated)
      return
    }

    onChange([
      ...selectedItems,
      {
        idProducto: product.id,
        [quantityField]: quantity,
        ...(priceField ? { [priceField]: draft.price } : {})
      }
    ])
  }

  function updateSelected(index, field, value) {
    onChange(selectedItems.map((item, currentIndex) => (
      currentIndex === index ? { ...item, [field]: value } : item
    )))
  }

  function removeSelected(index) {
    onChange(selectedItems.filter((_, currentIndex) => currentIndex !== index))
  }

  const selectedTotal = useMemo(() => {
    if (!showLineTotal) return 0
    return selectedItems.reduce((sum, item) => {
      const product = productById.get(String(item.idProducto))
      if (!product) return sum
      return sum + lineTotal({
        product: product.raw,
        quantity: item[quantityField],
        priceField,
        selectedPrice: priceField ? item[priceField] : undefined
      })
    }, 0)
  }, [priceField, productById, quantityField, selectedItems, showLineTotal])

  return (
    <div className="space-y-5">
      <section className="rounded-2xl border border-slate-200 bg-white p-4">
        <div className="mb-4">
          <h3 className="font-bold text-slate-950">{title}</h3>
          {description && <p className="mt-1 text-sm text-slate-500">{description}</p>}
        </div>

        <div className="mb-4 grid gap-3 md:grid-cols-[1fr_220px]">
          <Input
            label="Buscar"
            placeholder={searchPlaceholder}
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <Select label="Categoría" value={category} onChange={(event) => setCategory(event.target.value)}>
            <option value="">Todas</option>
            {categories.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </Select>
        </div>

        <div className="overflow-x-auto rounded-2xl border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Producto</th>
                <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Categoría</th>
                {showStock && <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">{stockLabel}</th>}
                {showUnitPrice && <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Precio</th>}
                <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">{quantityLabel}</th>
                {priceField && <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">{priceLabel}</th>}
                <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wide text-slate-500">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {filteredProducts.length === 0 ? (
                <tr>
                  <td colSpan={priceField ? 7 : 6} className="px-4 py-8 text-center text-sm text-slate-500">{emptyMessage}</td>
                </tr>
              ) : filteredProducts.map((product) => {
                const draft = getDraft(product)
                const alreadySelected = selectedIds.has(product.id)
                const stockBlocked = requireAvailableStock && product.stock !== null && product.stock <= 0
                const requestedQuantity = numberValue(draft.quantity)
                const exceedsStock = requireAvailableStock && product.stock !== null && requestedQuantity > product.stock
                const missingPrice = priceField && numberValue(draft.price) <= 0
                const disabled = stockBlocked || exceedsStock || missingPrice

                return (
                  <tr key={product.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm">
                      <p className="font-semibold text-slate-900">{product.name}</p>
                      <p className="text-xs text-slate-500">{product.code || 'Sin código'}</p>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600">{product.category}</td>
                    {showStock && (
                      <td className="px-4 py-3 text-sm">
                        <p className={`font-bold ${product.stock !== null && product.stock <= (product.stockMin || 0) ? 'text-red-600' : 'text-slate-900'}`}>
                          {product.stock ?? 'No definido'}
                        </p>
                        {showStockMin && <p className="text-xs text-slate-500">Mín: {product.stockMin ?? 0}</p>}
                      </td>
                    )}
                    {showUnitPrice && <td className="px-4 py-3 text-sm font-semibold text-slate-900">{formatMoney(product.price)}</td>}
                    <td className="px-4 py-3 text-sm">
                      <input
                        className="w-24 rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-400 focus:ring-4 focus:ring-slate-100"
                        type="number"
                        min="1"
                        step="1"
                        value={draft.quantity}
                        onChange={(event) => updateDraft(product.id, 'quantity', event.target.value)}
                      />
                    </td>
                    {priceField && (
                      <td className="px-4 py-3 text-sm">
                        <input
                          className="w-32 rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-400 focus:ring-4 focus:ring-slate-100"
                          type="number"
                          min="0.01"
                          step="0.01"
                          value={draft.price}
                          onChange={(event) => updateDraft(product.id, 'price', event.target.value)}
                        />
                      </td>
                    )}
                    <td className="px-4 py-3 text-right text-sm">
                      <Button type="button" className="px-3 py-2" disabled={disabled} onClick={() => addProduct(product)}>
                        {alreadySelected ? 'Sumar' : addButtonLabel}
                      </Button>
                      {disabled && (
                        <p className="mt-1 text-xs text-red-600">
                          {stockBlocked ? 'Sin stock' : exceedsStock ? 'Supera stock' : missingPrice ? 'Precio requerido' : ''}
                        </p>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div className="mb-4 flex flex-col justify-between gap-2 md:flex-row md:items-center">
          <div>
            <h3 className="font-bold text-slate-950">{selectedTitle}</h3>
            <p className="text-sm text-slate-500">Revisa cantidades antes de guardar.</p>
          </div>
          {showLineTotal && <p className="text-sm text-slate-500">Total seleccionado: <span className="font-black text-slate-950">{formatMoney(selectedTotal)}</span></p>}
        </div>

        <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-white">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Producto</th>
                <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">{quantityLabel}</th>
                {priceField && <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">{priceLabel}</th>}
                {showStock && <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Stock</th>}
                {showLineTotal && <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Total línea</th>}
                <th className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wide text-slate-500">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {selectedItems.length === 0 ? (
                <tr>
                  <td colSpan={priceField ? 6 : 5} className="px-4 py-8 text-center text-sm text-slate-500">{selectedEmptyMessage}</td>
                </tr>
              ) : selectedItems.map((item, index) => {
                const product = productById.get(String(item.idProducto))
                const quantity = item[quantityField]
                const line = product ? lineTotal({
                  product: product.raw,
                  quantity,
                  priceField,
                  selectedPrice: priceField ? item[priceField] : undefined
                }) : 0

                return (
                  <tr key={`${item.idProducto}-${index}`}>
                    <td className="px-4 py-3 text-sm">
                      <p className="font-semibold text-slate-900">{product?.name || `Producto #${item.idProducto}`}</p>
                      <p className="text-xs text-slate-500">{product?.code || 'Sin código'}</p>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <input
                        className="w-24 rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-400 focus:ring-4 focus:ring-slate-100"
                        type="number"
                        min="1"
                        step="1"
                        value={quantity}
                        onChange={(event) => updateSelected(index, quantityField, event.target.value)}
                      />
                    </td>
                    {priceField && (
                      <td className="px-4 py-3 text-sm">
                        <input
                          className="w-32 rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-400 focus:ring-4 focus:ring-slate-100"
                          type="number"
                          min="0.01"
                          step="0.01"
                          value={item[priceField]}
                          onChange={(event) => updateSelected(index, priceField, event.target.value)}
                        />
                      </td>
                    )}
                    {showStock && <td className="px-4 py-3 text-sm font-semibold text-slate-900">{product?.stock ?? '-'}</td>}
                    {showLineTotal && <td className="px-4 py-3 text-sm font-bold text-slate-950">{formatMoney(line)}</td>}
                    <td className="px-4 py-3 text-right text-sm">
                      <Button type="button" variant="danger" className="px-3 py-2" onClick={() => removeSelected(index)}>Quitar</Button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
