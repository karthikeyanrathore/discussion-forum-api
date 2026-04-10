const API_BASE_URL = "http://localhost:3000/api"

class ApiServicer {
    async makeRequest(endpoint, options={}){
        // TODO: add JWT auth
        const headers = {
            "Content-Type": "application/json",
            ...options.headers,
        };
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers,
            });
            const data = await response.json();

            if(!response.ok){
                throw new Error(data.message || `Request failed with status ${response.status}` );
            }
            return data;
        } catch (error){
            console.error("API error:", error);
            throw error;
        }
    }
}

nginxNotes = {
    getAll: () => this.makeRequest("/notes"),
    getById: (id) => this.makeRequest(`/notes/${id}`),
}

const api = new ApiServicer();
export default api;