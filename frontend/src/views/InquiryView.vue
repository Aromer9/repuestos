<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import InquiryForm from '../components/inquiry/InquiryForm.vue'
import { useInquiry } from '../composables/useInquiry.js'

const route = useRoute()
const { form, errors, loading, success, error, onRutInput, submitInquiry, years } = useInquiry()

onMounted(() => {
  if (route.query.marca) form.brand = route.query.marca
  if (route.query.modelo) form.model = route.query.modelo
  if (route.query.producto) form.description = `Necesito cotizar: ${decodeURIComponent(route.query.producto)}`
})

const updateForm = (newForm) => Object.assign(form, newForm)
</script>

<template>
  <div class="pt-[72px] min-h-screen bg-slate-50">

    <!-- Page header -->
    <div class="bg-white border-b border-slate-200 py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div class="inline-flex items-center gap-2 px-3 py-1.5 bg-[#E8F2FB] border border-[#0055A5]/20 rounded-full mb-4">
          <span class="w-1.5 h-1.5 rounded-full bg-[#0055A5] animate-pulse"></span>
          <span class="text-[#0055A5] text-xs font-semibold tracking-widest uppercase">Cotización gratuita</span>
        </div>
        <h1 class="text-3xl md:text-4xl font-bold text-slate-900 mb-3">Solicita tu cotización</h1>
        <p class="text-slate-500 max-w-xl mx-auto">
          Completa el formulario y un agente te contactará por WhatsApp con la mejor cotización del mercado.
        </p>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">

        <!-- Sidebar -->
        <div class="lg:col-span-1 order-2 lg:order-1">
          <div class="space-y-4 sticky top-24">

            <!-- Steps -->
            <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
              <h3 class="text-slate-900 font-semibold mb-5">¿Qué pasa después?</h3>
              <ol class="space-y-5">
                <li v-for="(step, i) in [
                  { title: 'Recibimos tu solicitud', desc: 'Verificamos los datos de tu vehículo usando el VIN.' },
                  { title: 'Cotizamos con proveedores', desc: 'Consultamos múltiples fuentes para darte el mejor precio.' },
                  { title: 'Te contactamos', desc: 'Recibirás un mensaje de WhatsApp con la cotización en menos de 24h.' },
                ]" :key="i" class="flex gap-3">
                  <div class="w-6 h-6 rounded-full bg-[#0055A5] text-white text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                    {{ i + 1 }}
                  </div>
                  <div>
                    <p class="text-slate-700 text-sm font-semibold">{{ step.title }}</p>
                    <p class="text-slate-500 text-xs mt-0.5">{{ step.desc }}</p>
                  </div>
                </li>
              </ol>
            </div>

            <!-- Trust -->
            <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-3">
              <div v-for="(item, i) in [
                { icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z', text: 'Tus datos están seguros' },
                { icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z', text: 'Cotización sin costo' },
                { icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z', text: 'Respuesta en menos de 24 horas' },
              ]" :key="i" class="flex items-center gap-3 text-sm">
                <svg class="w-4 h-4 text-[#0055A5] flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" :d="item.icon"/>
                </svg>
                <span class="text-slate-600">{{ item.text }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Form -->
        <div class="lg:col-span-2 order-1 lg:order-2">

          <!-- Success -->
          <div v-if="success" class="text-center py-16 bg-white border border-slate-200 rounded-xl shadow-sm px-8">
            <div class="w-20 h-20 bg-green-50 border border-green-200 rounded-3xl flex items-center justify-center mx-auto mb-6">
              <svg class="w-10 h-10 text-green-500" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-slate-900 mb-3">¡Solicitud recibida!</h2>
            <p class="text-slate-600 text-lg mb-2">
              Gracias, <span class="text-slate-900 font-semibold">{{ form.name.split(' ')[0] }}</span>.
            </p>
            <p class="text-slate-500 max-w-md mx-auto mb-8">
              Un agente te contactará por WhatsApp al
              <span class="text-slate-900 font-semibold">{{ form.phone }}</span> con la cotización.
            </p>
            <div class="bg-slate-50 border border-slate-200 rounded-xl p-5 text-left max-w-sm mx-auto mb-8">
              <h3 class="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-3">Resumen de tu solicitud</h3>
              <dl class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <dt class="text-slate-500">Vehículo</dt>
                  <dd class="text-slate-900 font-semibold">{{ form.brand }} {{ form.model }} {{ form.year }}</dd>
                </div>
                <div class="flex justify-between">
                  <dt class="text-slate-500">VIN</dt>
                  <dd class="text-slate-700 font-mono text-xs">{{ form.vin }}</dd>
                </div>
              </dl>
            </div>
            <router-link to="/" class="btn-secondary px-8 py-3">Volver al inicio</router-link>
          </div>

          <!-- Form panel -->
          <div v-else class="bg-white border border-slate-200 rounded-xl shadow-sm p-6 md:p-8">
            <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
              <p class="text-red-600 text-sm">{{ error }}</p>
            </div>
            <InquiryForm
              :form="form"
              :errors="errors"
              :loading="loading"
              :years="years"
              @update:form="updateForm"
              @rutInput="onRutInput"
              @submit="submitInquiry"
            />
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
