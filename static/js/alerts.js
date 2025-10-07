// Utility functions for SweetAlert2 notifications

const showSuccess = (title, message) => {
    Swal.fire({
        title: title,
        text: message,
        icon: 'success',
        confirmButtonText: 'OK',
        customClass: {
            container: 'swal-container',
            popup: 'swal-popup',
            confirmButton: 'swal-button'
        }
    });
};

const showError = (title, message) => {
    Swal.fire({
        title: title,
        text: message,
        icon: 'error',
        confirmButtonText: 'OK',
        customClass: {
            container: 'swal-container',
            popup: 'swal-popup',
            confirmButton: 'swal-button'
        }
    });
};

const showLoading = (message = 'Please wait...') => {
    Swal.fire({
        title: message,
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        },
        customClass: {
            container: 'swal-container',
            popup: 'swal-popup'
        }
    });
};

const closeLoading = () => {
    Swal.close();
};

const showConfirmation = async (title, message) => {
    const result = await Swal.fire({
        title: title,
        text: message,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Yes',
        cancelButtonText: 'No',
        customClass: {
            container: 'swal-container',
            popup: 'swal-popup',
            confirmButton: 'swal-button',
            cancelButton: 'swal-button'
        }
    });
    return result.isConfirmed;
};