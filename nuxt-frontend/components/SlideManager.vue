<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto py-10">
    <div class="bg-white rounded-lg shadow-lg w-full max-w-4xl max-h-full overflow-hidden flex flex-col">
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <h3 class="text-lg font-bold">Manage Homepage Slides</h3>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="p-4 overflow-y-auto flex-grow">
        <div class="mb-4 flex justify-end">
          <button 
            @click="addNewSlide" 
            class="btn btn-primary flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add Slide
          </button>
        </div>
        
        <div v-if="slides.length === 0" class="text-center py-10 text-gray-500">
          No slides yet. Please click the "Add Slide" button to create one.
        </div>
        
        <div v-else class="space-y-6">
          <div 
            v-for="(slide, index) in slides" 
            :key="slide.id"
            class="border border-gray-200 rounded-lg overflow-hidden"
          >
            <div class="bg-gray-50 p-3 flex justify-between items-center">
              <h4 class="font-medium">Slide #{{ index + 1 }}</h4>
              <div class="flex space-x-2">
                <button 
                  v-if="index > 0"
                  @click="moveSlide(index, -1)" 
                  class="text-gray-500 hover:text-gray-700 p-1"
                  title="Move Up"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                </button>
                <button 
                  v-if="index < slides.length - 1"
                  @click="moveSlide(index, 1)" 
                  class="text-gray-500 hover:text-gray-700 p-1"
                  title="Move Down"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </button>
                <button 
                  @click="removeSlide(index)" 
                  class="text-red-500 hover:text-red-700 p-1"
                  title="Delete"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div class="p-4 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
                  <input 
                    v-model="slide.title" 
                    type="text" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Slide title"
                  >
                </div>
                
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Subtitle</label>
                  <textarea 
                    v-model="slide.subtitle" 
                    rows="2"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Slide subtitle or description"
                  ></textarea>
                </div>
                
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Button Text</label>
                  <input 
                    v-model="slide.buttonText" 
                    type="text" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Button text"
                  >
                </div>
                
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Button Link</label>
                  <input 
                    v-model="slide.buttonLink" 
                    type="text" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="/categories"
                  >
                </div>
                
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Background Color</label>
                  <input 
                    v-model="slide.backgroundColor" 
                    type="text" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="bg-gradient-to-r from-primary-700 to-primary-900"
                  >
                  <p class="mt-1 text-xs text-gray-500">You can use Tailwind CSS color classes or gradient classes</p>
                </div>
              </div>
              
              <div>
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Background Image</label>
                  <div class="border border-gray-300 rounded-md p-4">
                    <div v-if="slide.backgroundImage" class="mb-4">
                      <img 
                        :src="slide.backgroundImage" 
                        alt="Background image preview" 
                        class="w-full h-40 object-cover rounded"
                      >
                      <button 
                        @click="slide.backgroundImage = ''" 
                        class="mt-2 text-sm text-red-500 hover:text-red-700"
                      >
                        Remove Image
                      </button>
                    </div>
                    
                    <div v-if="!slide.backgroundImage || uploadingImage === slide.id">
                      <input 
                        type="file" 
                        accept="image/*" 
                        @change="(e) => handleImageUpload(e, slide)"
                        class="w-full"
                      >
                      <p class="mt-1 text-xs text-gray-500">Recommended size: 1920x500 pixels</p>
                    </div>
                    
                    <div v-if="uploadingImage === slide.id" class="mt-2">
                      <div class="h-2 bg-gray-200 rounded">
                        <div 
                          class="h-full bg-primary-600 rounded" 
                          :style="`width: ${uploadProgress}%`"
                        ></div>
                      </div>
                      <p class="text-xs text-gray-500 mt-1">Uploading... {{ uploadProgress }}%</p>
                    </div>
                  </div>
                </div>
                
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Preview</label>
                  <div 
                    class="w-full h-40 rounded-md flex items-center justify-center overflow-hidden"
                    :class="slide.backgroundColor"
                    :style="slide.backgroundImage ? `background-image: url(${slide.backgroundImage}); background-size: cover; background-position: center;` : ''"
                  >
                    <div class="text-white text-center p-4 relative z-10">
                      <h4 class="text-xl font-bold">{{ slide.title || 'Slide Title' }}</h4>
                      <p class="text-sm mt-1">{{ slide.subtitle || 'Slide Subtitle' }}</p>
                      <button class="mt-2 px-3 py-1 bg-primary-600 text-white text-sm rounded">
                        {{ slide.buttonText || 'Button Text' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="p-4 border-t border-gray-200 flex justify-end space-x-2">
        <button 
          @click="$emit('close')" 
          class="px-4 py-2 border border-gray-300 rounded-md text-sm text-gray-700"
        >
          Cancel
        </button>
        <button 
          @click="saveSlides" 
          class="px-4 py-2 bg-primary-600 text-white rounded-md text-sm"
          :disabled="isSaving"
        >
          {{ isSaving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { v4 as uuidv4 } from 'uuid'

const props = defineProps({
  show: Boolean,
  initialSlides: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'save'])

// Slide data
const slides = ref([])
const isSaving = ref(false)
const uploadingImage = ref(null)
const uploadProgress = ref(0)

// Initialize slide data
onMounted(() => {
  slides.value = JSON.parse(JSON.stringify(props.initialSlides))
})

// Add new slide
const addNewSlide = () => {
  slides.value.push({
    id: uuidv4(),
    title: 'New Slide Title',
    subtitle: 'New Slide Subtitle',
    buttonText: 'Learn More',
    buttonLink: '/categories',
    backgroundColor: 'bg-gradient-to-r from-blue-700 to-indigo-900',
    backgroundImage: ''
  })
}

// Move slide position
const moveSlide = (index, direction) => {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= slides.value.length) return
  
  const temp = slides.value[index]
  slides.value[index] = slides.value[newIndex]
  slides.value[newIndex] = temp
}

// Remove slide
const removeSlide = (index) => {
  if (confirm('Are you sure you want to delete this slide?')) {
    slides.value.splice(index, 1)
  }
}

// Handle image upload
const handleImageUpload = async (event, slide) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Check file type
  if (!file.type.match('image.*')) {
    alert('Please select an image file')
    return
  }
  
  // Set uploading state
  uploadingImage.value = slide.id
  uploadProgress.value = 0
  
  try {
    // Create FormData
    const formData = new FormData()
    formData.append('image', file)
    
    // Upload to server
    const response = await fetch('/api/upload/image', {
      method: 'POST',
      body: formData,
      // Use XMLHttpRequest to track upload progress
      onUploadProgress: (progressEvent) => {
        uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      }
    })
    
    if (!response.ok) {
      throw new Error('Upload failed')
    }
    
    const data = await response.json()
    
    // Update slide with image URL
    slide.backgroundImage = data.url
  } catch (error) {
    console.error('Image upload error:', error)
    alert('Failed to upload image. Please try again.')
  } finally {
    // Reset upload state
    uploadingImage.value = null
    uploadProgress.value = 0
  }
}

// Save slides
const saveSlides = async () => {
  isSaving.value = true
  
  try {
    // Validate slides
    for (const slide of slides.value) {
      if (!slide.title) {
        alert('Please add a title for all slides')
        isSaving.value = false
        return
      }
    }
    
    // Send to parent component
    emit('save', slides.value)
    emit('close')
  } catch (error) {
    console.error('Save error:', error)
    alert('Failed to save slides. Please try again.')
  } finally {
    isSaving.value = false
  }
}
</script>
