// ***********************************************************
// This example support/index.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './home_page/commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

export function check_level(testLevel) {
    if (Cypress.env('level') < testLevel){
        cy.log(`Skipped! tests run on level ${Cypress.env('level')}.
        This test is on level ${Cypress.config('testLevel')}`)
        return true
    }
    return false
}