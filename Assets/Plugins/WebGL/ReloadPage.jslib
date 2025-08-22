mergeInto(LibraryManager.library, {
	ReloadPage: function() {
		if (typeof window !== 'undefined' && window.location && typeof window.location.reload === 'function') {
			window.location.reload();
		}
	}
});