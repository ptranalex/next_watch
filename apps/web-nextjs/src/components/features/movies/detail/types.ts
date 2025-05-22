import { Movie } from "@/domain/entities";

export interface MovieDetailViewProps {
  movie: Movie;
  isSignedIn: boolean;
  onUpdateMovie: (movie: Movie) => void;
}

export interface MovieRatings {
  imdb_rating: number | null;
  rotten_tomatoes_rating: number | null;
  metacritic_rating: number | null;
}
