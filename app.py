
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

# Create the Flask app
app = Flask(__name__)

# Enable CORS so other websites can use our API
CORS(app)

# Set up some basic config
app.config['SECRET_KEY'] = 'my-secret-key-for-development'
app.config['DEBUG'] = True

# This is the main page of our API
@app.route('/')
def home():
    """
    This shows when someone visits our API homepage
    """
    return jsonify({
        'message': 'Welcome to our Personality Analytics API!',
        'description': 'We predict if someone is Introvert or Extrovert',
        'made_by': '3 junior developers',
        'learning': 'Flask and APIs',
        'version': '1.0.0',
        'status': 'Working!',
        'available_endpoints': {
            'homepage': '/',
            'health_check': '/health', 
            'predict_personality': '/api/v1/predict',
            'predict_many': '/api/v1/predict/batch',
            'check_input': '/api/v1/validate',
            'api_help': '/api/v1/docs',
            'model_details': '/api/v1/model/info',
            'admin_page': '/api/v1/admin/stats'
        },
        'how_to_use': 'Visit /api/v1/docs for help'
    })

# Health check 
@app.route('/health')
def health_check():
    """
    Simple health check to see if our API is alive
    """
    return jsonify({
        'status': 'healthy',
        'message': 'API is working great!',
        'service_name': 'personality-analytics',
        'version': '1.0.0',
        'time_checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'environment': 'development'
    })

# Main prediction endpoint 
@app.route('/api/v1/predict', methods=['POST'])
def predict_personality():
    """
    Predict if someone is Introvert or Extrovert
    Send us personality scores and we'll tell you the result!
    """
    try:
        # Get the data from the request
        data = request.get_json()
        
        # Check if we got any data
        if not data:
            return jsonify({
                'error': 'Oops! You need to send us some data',
                'message': 'Please send personality scores in JSON format',
                'example': {
                    'Openness': 7.5,
                    'Conscientiousness': 8.2,
                    'Extraversion': 6.1,
                    'Agreeableness': 7.8,
                    'Neuroticism': 4.3
                }
            }), 400
        
        # List of personality traits we need
        required_traits = [
            'Openness', 
            'Conscientiousness', 
            'Extraversion', 
            'Agreeableness', 
            'Neuroticism'
        ]
        
        # Check if all required traits are provided
        missing_traits = []
        for trait in required_traits:
            if trait not in data:
                missing_traits.append(trait)
        
        if missing_traits:
            return jsonify({
                'error': 'Missing some personality traits!',
                'missing_traits': missing_traits,
                'required_traits': required_traits,
                'message': 'Please provide all 5 personality traits'
            }), 400
        
        # Check if the values are valid numbers (0-10 scale)
        for trait, value in data.items():
            if trait in required_traits:
                # Make sure it's a number
                if not isinstance(value, (int, float)):
                    return jsonify({
                        'error': f'The value for {trait} must be a number',
                        'received': f'{trait}: {value}',
                        'expected': 'A number between 0 and 10'
                    }), 400
                
                # Make sure it's between 0 and 10
                if value < 0 or value > 10:
                    return jsonify({
                        'error': f'The value for {trait} must be between 0 and 10',
                        'received': f'{trait}: {value}',
                        'valid_range': '0 to 10'
                    }), 400
        
        
        # Rrules to predict personality
        
        extraversion_score = data.get('Extraversion', 5)
        openness_score = data.get('Openness', 5)
        
        # Simple calculation 
        personality_calculation = (extraversion_score * 0.6) + (openness_score * 0.4)
        
        # Decide if person is Introvert or Extrovert
        if personality_calculation >= 6:
            predicted_personality = 'Extrovert'
            # Higher scores = higher confidence
            confidence = min(0.5 + (personality_calculation - 6) * 0.1, 0.95)
        else:
            predicted_personality = 'Introvert'
            # Lower scores = higher confidence for introvert
            confidence = min(0.5 + (6 - personality_calculation) * 0.1, 0.95)
        
        # Prepare the response
        result = {
            'data': {
                'prediction': {
                    'personality': predicted_personality,
                    'confidence': round(confidence, 3),
                    'calculation_score': round(personality_calculation, 2),
                    'probability_scores': {
                        'Extrovert': round(confidence if predicted_personality == 'Extrovert' else 1 - confidence, 3),
                        'Introvert': round(confidence if predicted_personality == 'Introvert' else 1 - confidence, 3)
                    },
                    'input_data': {trait: data[trait] for trait in required_traits},
                    'model_info': 'Simple rule-based model (we are learning!)',
                    'prediction_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            },
            'status': 'success',
            'message': 'Prediction completed successfully!'
        }
        
        # Print to console for debugging 
        print(f"New prediction: {predicted_personality} with {confidence:.2f} confidence")
        
        return jsonify(result), 200
        
    except Exception as e:
        # Something went wrong 
        print(f"Error in prediction: {str(e)}")  # Debug print
        return jsonify({
            'error': 'Something went wrong with the prediction',
            'details': str(e),
            'message': 'Please check your input and try again',
            'status': 'error'
        }), 500

# Batch prediction 
@app.route('/api/v1/predict/batch', methods=['POST'])
def batch_predict():
    """
    Predict personality for multiple people at the same time
    Useful when you have lots of data!
    """
    try:
        data = request.get_json()
        
        # Check if we got the right format
        if not data or 'samples' not in data:
            return jsonify({
                'error': 'Please send data in the right format',
                'expected_format': {
                    'samples': [
                        {'Openness': 7.5, 'Conscientiousness': 8.2, 'Extraversion': 6.1, 'Agreeableness': 7.8, 'Neuroticism': 4.3},
                        {'Openness': 4.1, 'Conscientiousness': 5.8, 'Extraversion': 3.2, 'Agreeableness': 6.1, 'Neuroticism': 7.2}
                    ]
                }
            }), 400
        
        samples = data['samples']
        
        # Make sure samples is a list
        if not isinstance(samples, list):
            return jsonify({
                'error': 'Samples must be a list of personality data',
                'received_type': str(type(samples))
            }), 400
        
        # Limit batch size 
        max_batch_size = 50  
        if len(samples) > max_batch_size:
            return jsonify({
                'error': f'Too many samples! Maximum is {max_batch_size}',
                'received': len(samples),
                'max_allowed': max_batch_size
            }), 400
        
        predictions = []
        successful_predictions = 0
        
        # Process each sample
        for i, sample in enumerate(samples):
            try:
                # Use simple prediction logic (same as single prediction)
                extraversion = sample.get('Extraversion', 5)
                openness = sample.get('Openness', 5)
                personality_score = (extraversion * 0.6) + (openness * 0.4)
                
                if personality_score >= 6:
                    personality = 'Extrovert'
                    confidence = min(0.5 + (personality_score - 6) * 0.1, 0.9)
                else:
                    personality = 'Introvert'
                    confidence = min(0.5 + (6 - personality_score) * 0.1, 0.9)
                
                predictions.append({
                    'sample_number': i + 1,
                    'status': 'success',
                    'prediction': {
                        'personality': personality,
                        'confidence': round(confidence, 3),
                        'input_data': sample
                    }
                })
                successful_predictions += 1
                
            except Exception as e:
                # If one sample fails vontinue with the rest
                predictions.append({
                    'sample_number': i + 1,
                    'status': 'failed',
                    'error': f'Could not process this sample: {str(e)}'
                })
        
        # Prepare batch results
        batch_results = {
            'data': {
                'batch_prediction': {
                    'total_samples': len(samples),
                    'successful_predictions': successful_predictions,
                    'failed_predictions': len(samples) - successful_predictions,
                    'success_rate': round(successful_predictions / len(samples), 2),
                    'predictions': predictions,
                    'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            },
            'status': 'completed',
            'message': f'Processed {len(samples)} samples successfully!'
        }
        
        print(f"Batch prediction completed: {successful_predictions}/{len(samples)} successful")
        return jsonify(batch_results), 200
        
    except Exception as e:
        print(f"Batch prediction error: {str(e)}")
        return jsonify({
            'error': 'Batch prediction failed',
            'details': str(e),
            'message': 'Please check your input format and try again'
        }), 500

# Input validation endpoint 
@app.route('/api/v1/validate', methods=['POST'])
def validate_input():
    """
    Check if your personality data is valid before making a prediction
    This helps catch errors early!
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'validation_result': {
                    'is_valid': False,
                    'errors': ['No data provided'],
                    'message': 'Please send some personality data to validate'
                }
            }), 200
        
        required_traits = ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism']
        errors = []
        warnings = []
        
        # Check for missing traits
        missing_traits = [trait for trait in required_traits if trait not in data]
        if missing_traits:
            errors.append(f"Missing required traits: {', '.join(missing_traits)}")
        
        # Check values for existing traits
        for trait, value in data.items():
            if trait in required_traits:
                # Check if it's a number
                if not isinstance(value, (int, float)):
                    errors.append(f"{trait} must be a number (received: {type(value).__name__})")
                else:
                    # Check range
                    if value < 0 or value > 10:
                        errors.append(f"{trait} must be between 0 and 10 (received: {value})")
                    elif value == 0 or value == 10:
                        warnings.append(f"{trait} is at extreme value ({value}) - are you sure?")
        
        # Check for extra traits (not errors, just info)
        extra_traits = [trait for trait in data.keys() if trait not in required_traits]
        if extra_traits:
            warnings.append(f"Extra traits will be ignored: {', '.join(extra_traits)}")
        
        is_valid = len(errors) == 0
        
        validation_result = {
            'validation_result': {
                'is_valid': is_valid,
                'errors': errors,
                'warnings': warnings,
                'input_data': data,
                'required_traits': required_traits,
                'message': 'Input is valid and ready for prediction!' if is_valid else 'Please fix the errors before making a prediction'
            },
            'status': 'validation_complete'
        }
        
        return jsonify(validation_result), 200
        
    except Exception as e:
        return jsonify({
            'validation_result': {
                'is_valid': False,
                'errors': [f'Validation failed: {str(e)}'],
                'message': 'Could not validate input'
            }
        }), 500

# API documentation - help for users
@app.route('/api/v1/docs')
def api_documentation():
    """
    Complete documentation for our API
    This explains how to use all our endpoints!
    """
    return jsonify({
        'api_documentation': {
            'title': 'Personality Analytics API Documentation',
            'version': '1.0.0',
            'description': 'Our first API for predicting personality types! Made by 3 junior developers.',
            'base_url': 'http://localhost:5000',
            'getting_started': {
                'step_1': 'Start with /health to check if API is working',
                'step_2': 'Use /api/v1/validate to check your data format',
                'step_3': 'Make predictions with /api/v1/predict',
                'step_4': 'For multiple predictions, use /api/v1/predict/batch'
            },
            'endpoints': {
                'homepage': {
                    'url': '/',
                    'method': 'GET',
                    'description': 'API homepage with basic info',
                    'example': 'curl http://localhost:5000/'
                },
                'health_check': {
                    'url': '/health',
                    'method': 'GET',
                    'description': 'Check if API is working',
                    'example': 'curl http://localhost:5000/health'
                },
                'predict_personality': {
                    'url': '/api/v1/predict',
                    'method': 'POST',
                    'description': 'Predict personality type from traits',
                    'required_data': {
                        'Openness': 'number 0-10',
                        'Conscientiousness': 'number 0-10',
                        'Extraversion': 'number 0-10',
                        'Agreeableness': 'number 0-10',
                        'Neuroticism': 'number 0-10'
                    },
                    'example_request': {
                        'Openness': 7.5,
                        'Conscientiousness': 8.2,
                        'Extraversion': 6.1,
                        'Agreeableness': 7.8,
                        'Neuroticism': 4.3
                    },
                    'example_curl': 'curl -X POST http://localhost:5000/api/v1/predict -H "Content-Type: application/json" -d \'{"Openness": 7.5, "Conscientiousness": 8.2, "Extraversion": 6.1, "Agreeableness": 7.8, "Neuroticism": 4.3}\''
                },
                'batch_predict': {
                    'url': '/api/v1/predict/batch',
                    'method': 'POST',
                    'description': 'Predict multiple personalities at once (max 50)',
                    'example_request': {
                        'samples': [
                            {'Openness': 7.5, 'Conscientiousness': 8.2, 'Extraversion': 6.1, 'Agreeableness': 7.8, 'Neuroticism': 4.3},
                            {'Openness': 4.1, 'Conscientiousness': 5.8, 'Extraversion': 3.2, 'Agreeableness': 6.1, 'Neuroticism': 7.2}
                        ]
                    }
                },
                'validate_input': {
                    'url': '/api/v1/validate',
                    'method': 'POST',
                    'description': 'Check if your data is valid before predicting',
                    'example_request': {'Openness': 7.5, 'Extraversion': 6.1}
                },
                'model_info': {
                    'url': '/api/v1/model/info',
                    'method': 'GET',
                    'description': 'Get information about our prediction model'
                }
            },
            'personality_types': {
                'Extrovert': 'Outgoing, social, energetic people',
                'Introvert': 'Thoughtful, independent, analytical people'
            },
            'tips_for_beginners': [
                'Always check /health first to make sure API is running',
                'Use /api/v1/validate to test your data format',
                'Personality scores should be between 0 and 10',
                'Higher Extraversion scores usually predict Extrovert',
                'Lower Extraversion scores usually predict Introvert',
                'Our model is still learning - we will make it smarter!'
            ],
            'common_errors': {
                '400': 'Bad input data - check the required format',
                '404': 'Endpoint not found - check your URL',
                '500': 'Server error - something went wrong on our side'
            }
        },
        'status': 'documentation_ready',
        'last_updated': datetime.now().strftime('%Y-%m-%d')
    })

# Model information endpoint
@app.route('/api/v1/model/info', methods=['GET'])
def model_info():
    """
    Information about our prediction model
    """
    return jsonify({
        'model_information': {
            'model_name': 'Simple Personality Predictor v1.0',
            'model_type': 'Rule-based (we are learning ML!)',
            'created_by': '3 junior developers',
            'accuracy': 'Still testing and improving',
            'features_used': [
                'Openness (creativity, imagination)',
                'Conscientiousness (organization, discipline)', 
                'Extraversion (social energy, outgoingness)',
                'Agreeableness (cooperation, trust)',
                'Neuroticism (emotional stability)'
            ],
            'prediction_classes': {
                'Extrovert': 'People who are outgoing and social',
                'Introvert': 'People who are thoughtful and independent'
            },
            'how_it_works': [
                'We take your 5 personality scores',
                'We focus mainly on Extraversion and Openness',
                'We calculate a simple score using basic math',
                'If score >= 6, we predict Extrovert',
                'If score < 6, we predict Introvert',
                'We also give you a confidence level'
            ],
            'limitations': [
                'This is our first model - very simple!',
                'We will add real machine learning later',
                'Currently only predicts 2 personality types',
                'Confidence calculation is basic'
            ],
            'future_improvements': [
                'Train with real data',
                'Add more personality types',
                'Use advanced machine learning',
                'Improve accuracy and confidence'
            ],
            'model_version': '1.0.0',
            'last_updated': '2025-06-19',
            'status': 'development'
        }
    })

# Admin statistics page
@app.route('/api/v1/admin/stats')
def admin_stats():
    """
    Basic statistics about our API
    """
    return jsonify({
        'service_statistics': {
            'service_name': 'Personality Analytics API',
            'version': '1.0.0',
            'created_by': '3 junior developers learning Flask',
            'project_status': 'Active development',
            'environment': 'GitHub Codespaces',
            'features_completed': [
                'Basic API structure',
                'Health checking',
                'Single personality prediction',
                'Batch prediction (up to 50)',
                'Input validation',
                'API documentation',
                'Error handling'
            ],
            'features_in_progress': [
                'Real machine learning model',
                'Database integration',
                'User authentication',
                'Better prediction accuracy'
            ],
            'technical_stack': {
                'backend': 'Flask (Python)',
                'cors': 'Flask-CORS',
                'deployment': 'GitHub Codespaces',
                'documentation': 'JSON API responses'
            },
            'api_limits': {
                'batch_prediction_max': 50,
                'personality_score_range': '0-10',
                'supported_personality_types': 2
            },
            'learning_journey': [
                'Started with basic Flask tutorials',
                'Learned about REST APIs and JSON',
                'Implemented error handling',
                'Added input validation',
                'Created comprehensive documentation'
            ],
            'next_goals': [
                'Integrate real ML model',
                'Add more personality types', 
                'Improve prediction accuracy',
                'Add user management',
                'Deploy to production'
            ]
        },
        'uptime_info': {
            'status': 'running',
            'started_at': 'When you ran python app.py',
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    })

# Error handlers - handle common errors nicely
@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors - when endpoint doesn't exist"""
    return jsonify({
        'error': 'Page not found',
        'message': 'The URL you requested does not exist',
        'available_endpoints': [
            '/ (homepage)',
            '/health (health check)',
            '/api/v1/predict (single prediction)',
            '/api/v1/predict/batch (multiple predictions)',
            '/api/v1/validate (check input)',
            '/api/v1/docs (documentation)',
            '/api/v1/model/info (model details)',
            '/api/v1/admin/stats (statistics)'
        ],
        'tip': 'Visit /api/v1/docs for complete documentation'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors - when something goes wrong on our side"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on our side',
        'what_to_do': [
            'Check if your input data is correct',
            'Try again in a few seconds',
            'If problem continues, check our /health endpoint'
        ],
        'support': 'This is a learning project by junior developers'
    }), 500

# Main execution
if __name__ == '__main__':
    print("Starting Personality Analytics API...")
    print("Made by: 3 junior developers")
    print("Learning: Flask, APIs, and Python")
    print("Environment: GitHub Codespaces")
    print("")
    print("Available endpoints:")
    print("   • Homepage: http://localhost:5000/")
    print("   • Health Check: http://localhost:5000/health")
    print("   • Predict: http://localhost:5000/api/v1/predict")
    print("   • Batch Predict: http://localhost:5000/api/v1/predict/batch")
    print("   • Validate Input: http://localhost:5000/api/v1/validate")
    print("   • Documentation: http://localhost:5000/api/v1/docs")
    print("   • Model Info: http://localhost:5000/api/v1/model/info")
    print("   • Admin Stats: http://localhost:5000/api/v1/admin/stats")
    print("")
    print("Tip: Visit http://localhost:5000/api/v1/docs for complete documentation")
    print("Debug mode: ON (perfect for learning!)")
    print("")
    
    # Create and run the app
    app.run(host='0.0.0.0', port=5000, debug=True)