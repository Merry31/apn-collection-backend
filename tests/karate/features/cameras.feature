Feature: Cameras API Validations

  Background:
    # Use full url directly to avoid path stripping issues causing 307 redirects
    * def baseCamerasUrl = baseUrl + '/cameras/'

  Scenario: Crud operations on a Camera
    # Create a new Camera
    Given url baseCamerasUrl
    And request { brand: 'KarateBrand', model: 'KarateModel', type: 'Digital SLR', year: 2026 }
    # Since we mocked Firebase Auth, we still need to send a dummy Bearer token to bypass the initial format check (Depends(security))
    And header Authorization = 'Bearer dummy_token'
    When method post
    Then status 201
    And match response.id == '#present'
    And match response.brand == 'KarateBrand'
    * def cameraId = response.id

    # Read the created Camera
    Given url baseCamerasUrl + cameraId
    And header Authorization = 'Bearer dummy_token'
    When method get
    Then status 200
    And match response.model == 'KarateModel'

    # Update the Camera
    Given url baseCamerasUrl + cameraId
    And request { brand: 'KarateBrandUpdated' }
    And header Authorization = 'Bearer dummy_token'
    When method put
    Then status 200
    And match response.brand == 'KarateBrandUpdated'

    # Delete the Camera
    Given url baseCamerasUrl + cameraId
    And header Authorization = 'Bearer dummy_token'
    When method delete
    Then status 204

    # Verify Deletion
    Given url baseCamerasUrl + cameraId
    And header Authorization = 'Bearer dummy_token'
    When method get
    Then status 404
