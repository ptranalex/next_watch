export interface Actor {
  id: number;
  name: string;
  profile_path?: string;
  character?: string;
  order?: number;
  biography?: string;
  birth_date?: string;
  death_date?: string;
  known_for_department?: string;
  place_of_birth?: string;
  popularity?: number;
  gender?: number;
  imdb_id?: string;
}

export default Actor;
