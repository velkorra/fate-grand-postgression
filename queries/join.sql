SELECT
    servant.id,
    servant.class,
    servant.name,
    servant.ascension_level,
    servant.level,
    ru_loc.name AS name_ru,
    ru_loc.description AS description_ru,
    ru_loc.history AS history_ru,
    ru_loc.prototype_person AS prototype_person_ru,
	ru_loc.illustrator as illustrator_ru,
	ru_loc.voice_actor as voice_actor_ru,
    en_loc.name AS name_en,
    en_loc.description AS description_en,
    en_loc.history AS history_en,
    en_loc.prototype_person AS prototype_person_en,
	en_loc.illustrator as illustrator_en,
	en_loc.voice_actor as voice_actor_en
FROM
    servant
LEFT JOIN servant_localization ru_loc
    ON servant.id = ru_loc.servant_id AND ru_loc.language = 'ru'
LEFT JOIN servant_localization en_loc
    ON servant.id = en_loc.servant_id AND en_loc.language = 'en';