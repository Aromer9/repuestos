<script setup>
import { BRANDS } from '../../data/products.js'

const props = defineProps({
  form: Object,
  errors: Object,
  loading: Boolean,
  years: Array,
})

const emit = defineEmits(['update:form', 'submit', 'rutInput'])

const updateField = (field, value) => {
  emit('update:form', { ...props.form, [field]: value })
}
</script>

<template>
  <form @submit.prevent="emit('submit')" class="space-y-8" novalidate>

    <!-- Section 1: Personal -->
    <div>
      <div class="flex items-center gap-2.5 mb-5">
        <span class="w-6 h-6 rounded-full bg-[#0055A5] text-white text-xs font-bold flex items-center justify-center">1</span>
        <h3 class="text-slate-600 text-xs font-semibold uppercase tracking-widest">Datos personales</h3>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="label">Nombre completo <span class="text-[#0055A5]">*</span></label>
          <input type="text" class="input-field" :class="errors.name ? '!border-red-400' : ''"
            placeholder="Ej: Juan Pérez González" :value="form.name"
            @input="updateField('name', $event.target.value)" />
          <p v-if="errors.name" class="mt-1.5 text-red-500 text-xs">{{ errors.name }}</p>
        </div>
        <div>
          <label class="label">RUT <span class="text-[#0055A5]">*</span></label>
          <input type="text" class="input-field font-mono" :class="errors.rut ? '!border-red-400' : ''"
            placeholder="Ej: 12.345.678-9" :value="form.rut" maxlength="12"
            @input="emit('rutInput', $event)" />
          <p v-if="errors.rut" class="mt-1.5 text-red-500 text-xs">{{ errors.rut }}</p>
        </div>
        <div>
          <label class="label">Teléfono / WhatsApp <span class="text-[#0055A5]">*</span></label>
          <input type="tel" class="input-field" :class="errors.phone ? '!border-red-400' : ''"
            placeholder="Ej: +56 9 1234 5678" :value="form.phone"
            @input="updateField('phone', $event.target.value)" />
          <p v-if="errors.phone" class="mt-1.5 text-red-500 text-xs">{{ errors.phone }}</p>
          <p v-else class="mt-1 text-slate-400 text-xs">Te contactaremos por este número.</p>
        </div>
        <div>
          <label class="label">Email <span class="text-slate-400 text-xs font-normal">(opcional)</span></label>
          <input type="email" class="input-field" placeholder="Ej: juan@correo.com"
            :value="form.email" @input="updateField('email', $event.target.value)" />
        </div>
      </div>
    </div>

    <div class="border-t border-slate-100"></div>

    <!-- Section 2: Vehicle -->
    <div>
      <div class="flex items-center gap-2.5 mb-5">
        <span class="w-6 h-6 rounded-full bg-[#0055A5] text-white text-xs font-bold flex items-center justify-center">2</span>
        <h3 class="text-slate-600 text-xs font-semibold uppercase tracking-widest">Datos del vehículo</h3>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label class="label">Marca <span class="text-[#0055A5]">*</span></label>
          <select class="input-field" :class="errors.brand ? '!border-red-400' : ''"
            :value="form.brand" @change="updateField('brand', $event.target.value)">
            <option value="" disabled>Seleccionar...</option>
            <option v-for="brand in BRANDS" :key="brand" :value="brand">{{ brand }}</option>
          </select>
          <p v-if="errors.brand" class="mt-1.5 text-red-500 text-xs">{{ errors.brand }}</p>
        </div>
        <div>
          <label class="label">Modelo <span class="text-[#0055A5]">*</span></label>
          <input type="text" class="input-field" :class="errors.model ? '!border-red-400' : ''"
            placeholder="Ej: Forester, Impreza..." :value="form.model"
            @input="updateField('model', $event.target.value)" />
          <p v-if="errors.model" class="mt-1.5 text-red-500 text-xs">{{ errors.model }}</p>
        </div>
        <div>
          <label class="label">Año <span class="text-[#0055A5]">*</span></label>
          <select class="input-field" :class="errors.year ? '!border-red-400' : ''"
            :value="form.year" @change="updateField('year', $event.target.value)">
            <option value="" disabled>Seleccionar...</option>
            <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
          </select>
          <p v-if="errors.year" class="mt-1.5 text-red-500 text-xs">{{ errors.year }}</p>
        </div>

        <!-- VIN full width -->
        <div class="sm:col-span-3">
          <label class="label">VIN — Número de chasis <span class="text-[#0055A5]">*</span></label>
          <input type="text" class="input-field font-mono tracking-widest uppercase" :class="errors.vin ? '!border-red-400' : ''"
            placeholder="Ej: JF1SJABC1GH000001" maxlength="17"
            :value="form.vin" @input="updateField('vin', $event.target.value.toUpperCase())" />
          <div class="flex items-center justify-between mt-1.5">
            <p v-if="errors.vin" class="text-red-500 text-xs">{{ errors.vin }}</p>
            <p v-else class="text-slate-400 text-xs">17 caracteres. Lo encuentras en el parabrisas o tarjeta de circulación.</p>
            <span class="text-slate-400 text-xs ml-auto">{{ form.vin.replace(/\s/g,'').length }}/17</span>
          </div>
        </div>
      </div>
    </div>

    <div class="border-t border-slate-100"></div>

    <!-- Section 3: Part -->
    <div>
      <div class="flex items-center gap-2.5 mb-5">
        <span class="w-6 h-6 rounded-full bg-[#0055A5] text-white text-xs font-bold flex items-center justify-center">3</span>
        <h3 class="text-slate-600 text-xs font-semibold uppercase tracking-widest">Repuesto solicitado</h3>
      </div>
      <div>
        <label class="label">Descripción del repuesto <span class="text-[#0055A5]">*</span></label>
        <textarea class="input-field resize-none" :class="errors.description ? '!border-red-400' : ''"
          rows="4" placeholder="Ej: Necesito las pastillas de freno delanteras, las actuales ya tienen el indicador encendido..."
          :value="form.description" @input="updateField('description', $event.target.value)"></textarea>
        <p v-if="errors.description" class="mt-1.5 text-red-500 text-xs">{{ errors.description }}</p>
        <p v-else class="mt-1.5 text-slate-400 text-xs">Mientras más detalles, mejor podemos cotizar.</p>
      </div>
    </div>

    <!-- Submit -->
    <button type="submit" class="btn-primary w-full py-4 text-base" :disabled="loading">
      <svg v-if="loading" class="w-5 h-5 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
      <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
      </svg>
      {{ loading ? 'Enviando solicitud...' : 'Enviar Solicitud de Cotización' }}
    </button>
    <p class="text-center text-slate-400 text-xs">Al enviar aceptas ser contactado por WhatsApp para tu cotización.</p>
  </form>
</template>
