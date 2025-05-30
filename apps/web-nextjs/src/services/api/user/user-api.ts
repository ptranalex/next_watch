import { fetchData, postData } from "../core/api-client";
import { APIClient } from "../core/api-client";
import { User, NetflixImportResult } from "./types";

/**
 * User API Client
 *
 * Provides methods to interact with user-related endpoints
 */
class UserAPI extends APIClient<User> {
  constructor() {
    super("/bff/v1/users");
  }

  /**
   * Get current user profile
   */
  getProfile = async (): Promise<User> => {
    return fetchData<User>(`${this.endpoint}/me`);
  };

  /**
   * Update user profile
   */
  updateProfile = async (userData: Partial<User>): Promise<User> => {
    return postData<User>(`${this.endpoint}/me`, userData);
  };

  /**
   * Import Netflix history CSV
   *
   * @param file The CSV file containing Netflix history
   * @returns Promise resolving to the import summary
   */
  importNetflixHistory = async (file: File): Promise<NetflixImportResult> => {
    const formData = new FormData();
    formData.append("file", file);

    // Use the API client's new uploadForm method
    return this.uploadForm<NetflixImportResult>(
      "/bff/v1/user/movies/import/netflix",
      formData
    );
  };
}

// Create and export a singleton instance
const userAPI = new UserAPI();
export default userAPI;
