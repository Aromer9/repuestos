import { ref, computed } from 'vue'
import { products as allProducts, BRANDS, CATEGORIES } from '../data/products.js'

export function useProducts() {
  const searchQuery = ref('')
  const selectedBrand = ref('')
  const selectedCategory = ref('')

  const filteredProducts = computed(() => {
    let result = allProducts

    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase()
      result = result.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.partNumber.toLowerCase().includes(q) ||
        p.brands.some(b => b.toLowerCase().includes(q)) ||
        p.models.some(m => m.toLowerCase().includes(q))
      )
    }

    if (selectedBrand.value) {
      result = result.filter(p => p.brands.includes(selectedBrand.value))
    }

    if (selectedCategory.value) {
      result = result.filter(p => p.category === selectedCategory.value)
    }

    return result
  })

  const getProductById = (id) => {
    return allProducts.find(p => p.id === Number(id)) || null
  }

  const resetFilters = () => {
    searchQuery.value = ''
    selectedBrand.value = ''
    selectedCategory.value = ''
  }

  return {
    searchQuery,
    selectedBrand,
    selectedCategory,
    filteredProducts,
    allProducts,
    brands: BRANDS,
    categories: CATEGORIES,
    getProductById,
    resetFilters,
  }
}
