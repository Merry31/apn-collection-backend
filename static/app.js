import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, signOut, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";

const API_BASE = '/api/v1/cameras';
const firebaseConfig = {
    apiKey: "AIzaSyDzP48q1O_qXqhmEEN8qONQRnsT24M5OIc",
    authDomain: "apn-collection-backend-d-9fa01.firebaseapp.com",
    projectId: "apn-collection-backend-d-9fa01",
    storageBucket: "apn-collection-backend-d-9fa01.firebasestorage.app",
    messagingSenderId: "925744932143",
    appId: "1:925744932143:web:d3465122813cfd4ca06dda"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

let currentUserToken = null;
let currentUserId = null;
// DOM Elements
const camerasGrid = document.getElementById('cameras-grid');
const cameraModal = document.getElementById('camera-modal');
const cameraForm = document.getElementById('camera-form');
const btnAddCamera = document.getElementById('btn-add-camera');
const btnCloseModal = document.getElementById('btn-close-modal');
const modalTitle = document.getElementById('modal-title');
const btnSaveCamera = document.getElementById('btn-save-camera');

// Auth DOM Elements
const btnAuth = document.getElementById('btn-auth');
const authBtnText = document.getElementById('auth-btn-text');
const userInfo = document.getElementById('user-info');

// Image Modal Elements
const imageModal = document.getElementById('image-modal');
const btnCloseImageModal = document.getElementById('btn-close-image-modal');
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const btnBrowseFile = document.getElementById('btn-browse-file');
const uploadPreview = document.getElementById('upload-preview');
const previewImg = document.getElementById('preview-img');
const fileNameDisplay = document.getElementById('file-name-display');
const btnConfirmUpload = document.getElementById('btn-confirm-upload');
const uploadCameraId = document.getElementById('upload-camera-id');

let selectedFile = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupAuthListeners();
    fetchCameras();
});

// --- Auth Interactions ---
function setupAuthListeners() {
    onAuthStateChanged(auth, async (user) => {
        if (user) {
            // User is signed in
            currentUserId = user.uid;
            currentUserToken = await user.getIdToken();

            authBtnText.textContent = "Sign Out";
            userInfo.textContent = user.email;
            userInfo.classList.remove('hidden');
            btnAddCamera.classList.remove('hidden');
        } else {
            // User is signed out
            currentUserId = null;
            currentUserToken = null;

            authBtnText.textContent = "Sign In";
            userInfo.classList.add('hidden');
            btnAddCamera.classList.add('hidden');
        }
        // Re-render cameras to hide/show edit/delete buttons based on auth state
        fetchCameras();
    });

    btnAuth.addEventListener('click', async () => {
        if (currentUserId) {
            // Sign out
            await signOut(auth);
        } else {
            // Sign in
            try {
                await signInWithPopup(auth, googleProvider);
            } catch (error) {
                console.error("Auth error", error);
                alert("Error signing in: " + error.message);
            }
        }
    });
}

// --- API Interactions ---

async function fetchCameras() {
    try {
        const response = await fetch(`${API_BASE}/`);
        if (!response.ok) throw new Error('Failed to fetch cameras');
        const cameras = await response.json();
        renderCameras(cameras);
    } catch (error) {
        console.error(error);
        camerasGrid.innerHTML = `<div class="loading-state" style="color: var(--danger)"><i class="fa-solid fa-triangle-exclamation" style="font-size: 2rem;"></i><p>Error loading collection.</p></div>`;
    }
}

async function saveCamera(cameraData, id = null) {
    const isUpdate = !!id;
    const url = isUpdate ? `${API_BASE}/${id}` : `${API_BASE}/`;
    const method = isUpdate ? 'PUT' : 'POST';

    const btnText = btnSaveCamera.querySelector('span');
    const btnSpinner = btnSaveCamera.querySelector('.btn-spinner');

    btnText.style.opacity = '0';
    btnSpinner.classList.remove('hidden');
    btnSaveCamera.disabled = true;

    try {
        const headers = { 'Content-Type': 'application/json' };
        if (currentUserToken) {
            // Re-fetch token to ensure it's fresh
            currentUserToken = await auth.currentUser.getIdToken();
            headers['Authorization'] = `Bearer ${currentUserToken}`;
        }

        const response = await fetch(url, {
            method: method,
            headers: headers,
            body: JSON.stringify(cameraData)
        });

        if (!response.ok) throw new Error('Failed to save camera');

        closeModal();
        fetchCameras(); // refresh list
    } catch (error) {
        console.error(error);
        alert('Error saving camera.');
    } finally {
        btnText.style.opacity = '1';
        btnSpinner.classList.add('hidden');
        btnSaveCamera.disabled = false;
    }
}

async function deleteCamera(id) {
    if (!confirm('Are you sure you want to delete this camera?')) return;

    try {
        const headers = {};
        if (currentUserToken) {
            currentUserToken = await auth.currentUser.getIdToken();
            headers['Authorization'] = `Bearer ${currentUserToken}`;
        }
        const response = await fetch(`${API_BASE}/${id}`, {
            method: 'DELETE',
            headers: headers
        });
        if (!response.ok) throw new Error('Failed to delete camera');
        fetchCameras();
    } catch (error) {
        console.error(error);
        alert('Error deleting camera.');
    }
}

async function uploadImage() {
    if (!selectedFile) return;

    const id = uploadCameraId.value;
    const formData = new FormData();
    formData.append('file', selectedFile);

    const btnText = btnConfirmUpload.querySelector('span');
    const btnSpinner = btnConfirmUpload.querySelector('.btn-spinner');

    btnText.style.opacity = '0';
    btnSpinner.classList.remove('hidden');
    btnConfirmUpload.disabled = true;

    try {
        const headers = {};
        if (currentUserToken) {
            currentUserToken = await auth.currentUser.getIdToken();
            headers['Authorization'] = `Bearer ${currentUserToken}`;
        }

        const response = await fetch(`${API_BASE}/${id}/images`, {
            method: 'POST',
            headers: headers,
            body: formData
        });

        if (!response.ok) throw new Error('Failed to upload image');

        closeImageModal();
        fetchCameras(); // refresh to show new image
    } catch (error) {
        console.error(error);
        alert('Error uploading image.');
    } finally {
        btnText.style.opacity = '1';
        btnSpinner.classList.add('hidden');
        btnConfirmUpload.disabled = false;
    }
}

// --- UI Rendering ---

function renderCameras(cameras) {
    if (cameras.length === 0) {
        camerasGrid.innerHTML = `
            <div class="loading-state">
                <i class="fa-solid fa-camera" style="font-size: 3rem; color: var(--text-muted); opacity: 0.5;"></i>
                <p>Your collection is empty. Add your first camera!</p>
            </div>`;
        return;
    }

    camerasGrid.innerHTML = cameras.map(cam => {
        // Use first image if exists, otherwise show placeholder
        const hasImage = cam.image_urls && cam.image_urls.length > 0;
        const imgContent = hasImage
            ? `<img src="${cam.image_urls[cam.image_urls.length - 1]}" alt="${cam.brand} ${cam.model}">`
            : `<i class="fa-solid fa-camera placeholder"></i>`;

        return `
            <article class="camera-card glass-panel html-tag-data-target" data-id="${cam.id}">
                <div class="card-image">
                    ${imgContent}
                    ${currentUserId ? `
                    <div class="image-overlay">
                        <button class="btn-primary btn-add-image" onclick="openImageModal('${cam.id}')">
                            <i class="fa-solid fa-upload"></i> Upload
                        </button>
                    </div>` : ''}
                </div>
                <div class="card-content">
                    <div class="card-brand">${cam.brand}</div>
                    <h3 class="card-model">${cam.model}</h3>
                    
                    <div class="card-badges">
                        <span class="badge"><i class="fa-solid fa-tag"></i> ${cam.type}</span>
                        ${cam.year ? `<span class="badge"><i class="fa-regular fa-calendar"></i> ${cam.year}</span>` : ''}
                        ${cam.format ? `<span class="badge"><i class="fa-solid fa-film"></i> ${cam.format}</span>` : ''}
                    </div>

                    ${cam.notes ? `<p class="card-notes">${cam.notes}</p>` : '<p class="card-notes"><em>No notes</em></p>'}

                    ${currentUserId ? `
                    <div class="card-actions">
                        <button class="btn-secondary btn-edit" onclick='openEditModal(${JSON.stringify(cam).replace(/'/g, "&#39;")})'>
                            <i class="fa-solid fa-pen"></i> Edit
                        </button>
                        <button class="btn-danger btn-delete" onclick="deleteCamera('${cam.id}')">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>` : ''}
                </div>
            </article>
        `;
    }).join('');
}

// --- Event Listeners & Modals ---

// Add/Edit Modal
btnAddCamera.addEventListener('click', () => {
    cameraForm.reset();
    document.getElementById('camera-id').value = '';
    modalTitle.textContent = 'Add New Camera';
    cameraModal.classList.add('active');
});

btnCloseModal.addEventListener('click', closeModal);
cameraModal.addEventListener('click', (e) => {
    if (e.target === cameraModal) closeModal();
});

function closeModal() {
    cameraModal.classList.remove('active');
}

window.openEditModal = function (cam) {
    document.getElementById('camera-id').value = cam.id;
    document.getElementById('brand').value = cam.brand;
    document.getElementById('model').value = cam.model;
    document.getElementById('type').value = cam.type;
    document.getElementById('year').value = cam.year || '';
    document.getElementById('format').value = cam.format || '';
    document.getElementById('condition').value = cam.condition || '';
    document.getElementById('notes').value = cam.notes || '';

    modalTitle.textContent = 'Edit Camera';
    cameraModal.classList.add('active');
};

cameraForm.addEventListener('submit', (e) => {
    e.preventDefault();

    // Convert year to int or null
    let yearVal = document.getElementById('year').value;
    yearVal = yearVal ? parseInt(yearVal, 10) : null;

    const cameraData = {
        brand: document.getElementById('brand').value,
        model: document.getElementById('model').value,
        type: document.getElementById('type').value,
        year: yearVal,
        format: document.getElementById('format').value || null,
        condition: document.getElementById('condition').value || null,
        notes: document.getElementById('notes').value || null
    };

    const id = document.getElementById('camera-id').value;
    saveCamera(cameraData, id);
});


// Image Upload Modal
window.openImageModal = function (id) {
    uploadCameraId.value = id;
    resetUploadState();
    imageModal.classList.add('active');
};

btnCloseImageModal.addEventListener('click', closeImageModal);
imageModal.addEventListener('click', (e) => {
    if (e.target === imageModal) closeImageModal();
});

function closeImageModal() {
    imageModal.classList.remove('active');
    resetUploadState();
}

function resetUploadState() {
    selectedFile = null;
    uploadArea.classList.remove('hidden');
    uploadPreview.classList.add('hidden');
    btnConfirmUpload.disabled = true;
    fileInput.value = '';
}

btnBrowseFile.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
    }
});

// Drag and drop setup
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        handleFileSelection(e.dataTransfer.files[0]);
    }
});

function handleFileSelection(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file.');
        return;
    }

    selectedFile = file;
    fileNameDisplay.textContent = file.name;

    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        uploadArea.classList.add('hidden');
        uploadPreview.classList.remove('hidden');
        btnConfirmUpload.disabled = false;
    };
    reader.readAsDataURL(file);
}

btnConfirmUpload.addEventListener('click', uploadImage);
