import { Actor as ServiceActor } from "@/services/api/common/types";

/**
 * UI-friendly Actor entity extending the API service type.
 * Used in components and UI state management.
 *
 * This type:
 * 1. Adds UI-specific helper properties
 * 2. Normalizes naming conventions for the UI
 * 3. Provides type safety for the application domain
 *
 * @interface Actor
 * @extends {Omit<ServiceActor, "birthday">}
 */
export interface Actor extends Omit<ServiceActor, "birthday"> {
  /**
   * Actor's birth date (renamed from birthday for consistency)
   * @type {string}
   * @memberof Actor
   */
  birth_date?: string;

  /**
   * Actor's date of death (if applicable)
   * @type {string}
   * @memberof Actor
   */
  death_date?: string;

  /**
   * Character name when used in movie cast context
   * @type {string}
   * @memberof Actor
   */
  character?: string;

  /**
   * Display order when used in cast lists
   * @type {number}
   * @memberof Actor
   */
  order?: number;

  /**
   * UI state: whether the actor is selected in a list/grid view
   * @type {boolean}
   * @memberof Actor
   */
  isSelected?: boolean;

  /**
   * Alternative display name for UI (e.g., "Character name (Actor name)")
   * @type {string}
   * @memberof Actor
   */
  displayName?: string;
}

/**
 * Helper function to convert a service actor to a UI entity
 *
 * @param {ServiceActor} serviceActor - The API service actor object
 * @returns {Actor} A UI-friendly actor entity
 */
export function toActorEntity(serviceActor: ServiceActor): Actor {
  return {
    ...serviceActor,
    birth_date: serviceActor.birthday,
  };
}

/**
 * Helper function to convert a UI entity back to a service actor
 *
 * @param {Actor} actor - The UI actor entity
 * @returns {Partial<ServiceActor>} A service-compatible actor object
 */
export function toServiceActor(actor: Actor): Partial<ServiceActor> {
  const { birth_date, death_date, isSelected, displayName, ...serviceProps } =
    actor;

  return {
    ...serviceProps,
    birthday: birth_date,
  };
}
