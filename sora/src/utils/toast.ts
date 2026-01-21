import { reactive } from 'vue'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

interface Toast {
    id: number
    message: string
    type: ToastType
    duration?: number
}

export const toastState = reactive({
    toasts: [] as Toast[]
})

let toastId = 0

export const toast = {
    show(message: string, type: ToastType = 'info', duration: number = 3000) {
        const id = toastId++
        const newToast: Toast = { id, message, type, duration }
        toastState.toasts.push(newToast)

        if (duration > 0) {
            setTimeout(() => {
                this.remove(id)
            }, duration)
        }
        return id
    },

    success(message: string, duration?: number) {
        return this.show(message, 'success', duration)
    },

    error(message: string, duration?: number) {
        return this.show(message, 'error', duration)
    },

    info(message: string, duration?: number) {
        return this.show(message, 'info', duration)
    },

    warning(message: string, duration?: number) {
        return this.show(message, 'warning', duration)
    },

    remove(id: number) {
        const index = toastState.toasts.findIndex(t => t.id === id)
        if (index !== -1) {
            toastState.toasts.splice(index, 1)
        }
    }
}
